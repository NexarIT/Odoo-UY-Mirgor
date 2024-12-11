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


class MercadoLibreLogIn(http.Controller):

    @http.route(['/mercadolibre_log_in'], type='http', auth="user", methods=['GET'], website=True)
    def meli_login(self, **kwargs):
        company = request.env.company
        meli = company.mercadolibre_configuration_id.get_mercadolibre_lib()
        redirect_uri = company.mercadolibre_redirect_uri
        if not kwargs:
            kwargs = {}
        if kwargs.get('error'):
            message = "ERROR: %s" % kwargs.get('error')
            return "<h1>"+message+"</h1><br/><a href='"+meli.auth_url(redirect_uri)+"'>Login</a>"
        if kwargs.get('code'):
            meli.authorize(kwargs.get('code'), redirect_uri)
            company.write({
                'mercadolibre_access_token': meli.access_token,
                'mercadolibre_refresh_token': meli.refresh_token,
            })
            return """
            <div>
                <b>Autenticado!</b><br/>
                <b>Application id:</b>  {}<br/>
                <b>Access token:</b> {}<br/>
                <b>Refresh Token:</b> {}
            </div>
            <a href="javascript:window.history.go(-2);">Volver a Odoo</a> <script>window.history.go(-2)</script>
            """.format(kwargs.get('code'), meli.access_token, meli.refresh_token)
        else:
            return "<a href='"+meli.auth_url(redirect_uri)+"'>Login</a>"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
