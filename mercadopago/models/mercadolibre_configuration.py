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

from odoo import models
from mercadolibre.src import mercadopago as mp


class MercadolibreConfiguration(models.Model):
    _inherit = 'mercadolibre.configuration'

    def get_mercadopago_lib(self):
        self.ensure_one()
        return mp.Mercadopago(
            client_id=self.mercadolibre_client_id,
            client_secret=self.mercadolibre_client_secret,
            access_token=self.mercadolibre_access_token,
            refresh_token=self.mercadolibre_refresh_token
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
