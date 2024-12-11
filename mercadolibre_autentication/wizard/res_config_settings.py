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


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    mercadolibre_client_id = fields.Char(
        'Mercadolibre client ID',
        related='mercadolibre_configuration_id.mercadolibre_client_id',
        readonly=False
    )
    mercadolibre_client_secret = fields.Char(
        'Mercadolibre client secret',
        related='mercadolibre_configuration_id.mercadolibre_client_secret',
        readonly=False
    )
    mercadolibre_access_token = fields.Char(
        'Mercadolibre access token',
        related='mercadolibre_configuration_id.mercadolibre_access_token',
    )
    mercadolibre_refresh_token = fields.Char(
        'Mercadolibre refresh token',
        related='mercadolibre_configuration_id.mercadolibre_refresh_token',
    )
    mercadolibre_redirect_uri = fields.Char(
        'Mercadolibre redirect_uri token',
        related='mercadolibre_configuration_id.mercadolibre_redirect_uri',
        readonly=False
    )
    mercadolibre_user_id = fields.Char(
        'Mercadolibre user ID',
        related='mercadolibre_configuration_id.mercadolibre_user_id',
        readonly=False
    )
    mercadolibre_country_id = fields.Many2one(
        string='País de la configuración',
        related='mercadolibre_configuration_id.mercadolibre_country_id',
        readonly=False
    )

    def mercadolibre_log_in(self):
        return self.mercadolibre_configuration_id.log_in()

    def mercadolibre_log_out(self):
        return self.mercadolibre_configuration_id.log_out()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
