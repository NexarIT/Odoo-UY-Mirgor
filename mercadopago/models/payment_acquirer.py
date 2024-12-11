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

from odoo import models, fields


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('mercadopago', "MercadoPago")],
        ondelete={'mercadopago': 'set default'}
    )

    def mercadopago_get_form_action_url(self):
        """ Defino a qué URL se redirigirá al usuario cuando llegue el momento de efectuar el pago """
        self.ensure_one()
        current_website = self.env['website'].sudo().get_current_website()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = current_website.domain if current_website and current_website.domain else base_url
        url = url.rstrip('/')
        return url + \
            ("/mercadopago_send_prod" if self.state == 'enabled' else "/mercadopago_send_test")
    
    def _get_default_payment_method_id(self):
        """Devuelve el método de pago correspondiente si el acquirer
        es mercadopago

        :return: Método de pago
        :rtype: account.payment.method
        """        
        self.ensure_one()
        if self.provider != 'mercadopago':
            return super()._get_default_payment_method_id()
        return self.env.ref('mercadopago.payment_method_mercadopago').id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
