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

from odoo import http
from odoo.http import request
import werkzeug


class MercadoPagoRedirect(http.Controller):

    @http.route(['/mercadopago_redirect/success'], type='http', auth="public", website=True)
    def redirect_success(self, **post):
        """
        Si un pago de MercadoPago disparado desde e-commerce fue exitoso, redirige al usuario al e-commerce para
        concluir la transacción
        """
        request.env['payment.transaction'].sudo()._handle_feedback_data('mercadopago', post)
        return werkzeug.utils.redirect('/payment/status')

    @http.route(['/mercadopago_redirect/failure'], type='http', auth="public", website=True)
    def redirect_failure(self, **post):
        """
        Si un pago de MercadoPago disparado desde e-commerce fue fallido o cancelado, redirige al usuario al checkout
        del e-commerce
        """
        return werkzeug.utils.redirect('/shop/payment')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
