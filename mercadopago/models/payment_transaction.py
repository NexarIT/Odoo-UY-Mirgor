# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import mercadolibre.src.mercadopago_merchant_order as mp_mo


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    acquirer_journal_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda del diario del medio de pago',
        compute='_compute_acquirer_journal_currency_id',
        store=True,
    )
    amount_acquirer_journal_currency = fields.Monetary(
        string='Monto en moneda diario',
        help='Monto expresado en la moneda del diario del medio de pago',
        currency_field='acquirer_journal_currency_id',
        compute='_compute_amount_acquirer_journal_currency',
        store=True,
    )

    @api.depends(
            'acquirer_id.journal_id.currency_id',
            'company_id.currency_id',
    )
    def _compute_acquirer_journal_currency_id(self):
        """Calcula la moneda del diario del medio de pago.
        En caso de no tener será la moneda de la compañía
        """        
        for record in self:
            record.acquirer_journal_currency_id = record.acquirer_id.journal_id.currency_id or record.company_id.currency_id

    @api.depends(
            'acquirer_id.journal_id.currency_id',
            'currency_id',
            'company_id',
            'amount',
            'create_date'
    )
    def _compute_amount_acquirer_journal_currency(self):
        """Calcula el monto en la moneda del diario del medio de pago
        """        
        for record in self:
            record.amount_acquirer_journal_currency = record.currency_id._convert(
                record.amount,
                record.acquirer_journal_currency_id,
                record.company_id,
                fields.Date.to_date(record.create_date)
            )

    def _mercadopago_check_if_paid(self, mo_data):
        self.ensure_one()
        # Si el pago está vinculado a otra transacción
        if mo_data.get('external_reference') != self.reference:
            return False
        # Modo prod
        if self.env.ref('mercadopago.payment_acquirer_mercadopago').state == 'enabled':
            return mo_data.get('status') == 'closed' and mo_data.get('order_status') == 'paid'
        # Modo test
        return mo_data.get('status') == 'opened' and mo_data.get('order_status') == 'payment_required'

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Se busca la transacción de Odoo en base a la referencia recibida en el response de MercadoPago """
        if provider != 'mercadopago':
            return super()._get_tx_from_feedback_data(provider, data)
        if not data.get('external_reference'):
            raise ValidationError("MercadoPago: No se recibió external_reference")
        return self.search([('reference', '=', data['external_reference'])], limit=1)

    def _process_feedback_data(self, data):
        """ Se evalúan los datos recibidos para determinar si el pago se realizó correctamente o no """
        if self.provider != 'mercadopago':
            return super()._process_feedback_data(data)
        merchant_order = data.get('merchant_order_id')
        if not merchant_order:
            raise ValidationError("MercadoPago: No se recibió merchant_order_id")
        sale_companies = self.sale_order_ids.mapped('company_id')
        company = sale_companies if len(sale_companies) == 1 else self.env.company
        mp = company.mercadolibre_configuration_ids[0].get_mercadopago_lib()
        mo_data = mp_mo.get_merchant_order_data(mp, merchant_order)
        self.write({'acquirer_reference': merchant_order})
        if self._mercadopago_check_if_paid(mo_data):
            self._set_done()

    def _get_specific_rendering_values(self, processing_values):
        """Herencia para retornar valores específicos de MercadoPago

        :param processing_values: Los valores genéricos y específicos de la transacción
        :type processing_values: dict
        :return: Diccionario con los valores específicos del payment.acquirer
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'mercadopago':
            return res
        processing_values.update({
            'mercadopago_url': self.acquirer_id.mercadopago_get_form_action_url(),
            'currency_id': self.acquirer_journal_currency_id.id,
            'currency': self.acquirer_journal_currency_id.name,
            'amount': self.amount_acquirer_journal_currency,
        })
        return processing_values
    
    def _reconcile_after_done(self):
        """Se hereda método para cambiar los montos y moneda utilizados en la factura,
        por los que corresponden al diario del medio de pago.

        :return: None
        :rtype: NoneType
        """        
        if self.provider == 'mercadopago' and self.invoice_ids:
            # Nos quedamos con las facturas en borrador
            invoices = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
            # Seteamos por contexto que no se chequee la validez del asiento
            # para poder cambiar los importes sin errores
            for invoice in invoices.with_context(check_move_validity=False):
                lines = invoice.mapped('invoice_line_ids')
                # Guardamos la moneda actual de la factura
                invoice_currency = invoice.currency_id
                # Actualizamos la moneda con la del diario del medio de pago
                invoice.write({'currency_id': self.acquirer_journal_currency_id.id})
                invoice._onchange_currency()
                # Ante el cambio de moneda cambiamos la cuenta contable de deudores
                invoice._onchange_invoice_partner_id()
                # Cambiamos los precios unitarios
                for line in lines:
                    price_unit = invoice_currency._convert(
                        line.price_unit,
                        self.acquirer_journal_currency_id,
                        line.company_id,
                        line.date
                    )
                    line.write({
                        'price_unit': price_unit,
                    })
                    line._onchange_price_subtotal()
                # Recalculamos el resto de apuntes, incluidos los de impuestos
                invoice._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        return super()._reconcile_after_done()
    
    def _create_payment(self, **extra_create_values):
        """Se hereda método para cambiar los montos y moneda utilizados,
        por los que corresponden al diario del medio de pago.

        :return: Pago generado
        :rtype: account.payment
        """        
        self.ensure_one()
        if self.provider == 'mercadopago':
            extra_create_values.update(
                {
                    'amount': abs(self.amount_acquirer_journal_currency),
                    'currency_id': self.acquirer_journal_currency_id.id,
                }
            )
        return super()._create_payment(**extra_create_values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
