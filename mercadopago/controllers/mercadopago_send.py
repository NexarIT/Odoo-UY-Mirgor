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

import werkzeug

from odoo import http
from odoo.http import request

from mercadolibre.src import error_handler


class MercadoPagoSend(http.Controller):
    def update_config_token(self, config):
        """ Método auxiliar para actualizar los tokens de ML con el cursor actual en vez de uno nuevo """
        token_data = config._get_mercadolibre_service().get_token_refresh()
        token_data = config._eval_meli_service_response(token_data)
        config.write({
            'mercadolibre_refresh_token': token_data.get('refresh_token'),
            'mercadolibre_access_token': token_data.get('access_token'),
        })

    def send_to_mercadopago(self, data):
        """
        Prepara el request a enviar a MercadoPago y lo envía, devolviendo el response obtenido
        @param data: diccionario con la referencia del pago de e-commerce, la moneda (ej.: "ARS") y el monto
        """
        config = request.env.company.sudo().mercadolibre_configuration_ids[0]
        vals = self.get_mercadopago_vals(data)
        res = False
        while not res:
            mp = config.get_mercadopago_lib()
            try:
                res = mp.post_with_token('/checkout/preferences', vals)
                false = False
                null = None
                eval_res = eval(res.content)
                if isinstance(eval_res, dict) and eval_res.get('code') == 'unauthorized':
                    self.update_config_token(config)
                    res = False
                else:
                    error_handler.RestErrorHandler.handle_error(res)
            except error_handler.InvalidTokenException:
                self.update_config_token(config)
                res = False
        false = False
        null = None
        return eval(res.content)

    def get_mercadopago_vals(self, data):
        """
        Obtengo un diccionario con los valores que se enviarán a MercadoPago
        @param data: diccionario con la referencia del pago de e-commerce, la moneda (ej.: "ARS") y el monto
        """
        current_website = request.env['website'].sudo().get_current_website()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = current_website.domain if current_website and current_website.domain else base_url
        url = url.rstrip('/')
        payment_transaction = request.env['payment.transaction'].sudo().search([('reference', '=', data['reference'])])
        vals = {
            'items': [{
                'title': "Orden E-Commerce " + data['reference'],
                'quantity': 1,
                'currency_id': payment_transaction.acquirer_journal_currency_id.name,
                'unit_price': payment_transaction.amount_acquirer_journal_currency,
            }],
            'back_urls': {
                "success": url + "/mercadopago_redirect/success",
                "failure": url + "/mercadopago_redirect/failure",
            },
            'auto_return': "all",
            'external_reference': data['reference'],
            'payment_methods': {
                'excluded_payment_types': [{'id': 'ticket'}, {'id': 'bank_transfer'}]
            }
        }
        return vals

    @http.route(['/mercadopago_send_test'], type='http', auth="public", csrf=False)
    def send_to_mercadopago_test(self, **post):
        """ Envía los datos a MercadoPago y redirige al usuario a la interfaz de pago sandbox (test) de MercadoPago """
        data = self.send_to_mercadopago(post)
        return werkzeug.utils.redirect(data['sandbox_init_point'])

    @http.route(['/mercadopago_send_prod'], type='http', auth="public", csrf=False)
    def send_to_mercadopago_prod(self, **post):
        """ Envía los datos a MercadoPago y redirige al usuario a la interfaz de pago real de MercadoPago """
        data = self.send_to_mercadopago(post)
        return werkzeug.utils.redirect(data['init_point'])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
