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

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSaleCurrency(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        vals = super(WebsiteSaleCurrency, self)._get_shop_payment_values(order)
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(
                            pricelist_context['pricelist'])
        acquirers = []
        # Si la moneda en la lista de precios no coincide con la de la compañia
        # hago un filtro para evitar pagos desde mercadopago
        if pricelist.currency_id.id != request.env.company.currency_id.id:
            for acq in vals.get('acquirers', list()):
                if acq.id == request.env.ref('mercadopago.payment_acquirer_mercadopago').id:
                    continue
                acquirers.append(acq)
            vals.update(
                acquirers=acquirers,
            )
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
