# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{

    'name': 'Mercadolibre autentication',

    'version': '2.0.1',

    'category': 'Mercadolibre',

    'summary': 'Autenticación para mercadolibre',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'AGPL-3',

    'depends': [
        'mercadolibre_base'
    ],

    'data': [
        
        'data/ir_cron.xml',
        'data/res_country.xml',
        'views/res_country.xml',
        'wizard/res_config_settings.xml',
    
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Autenticación para mercadolibre',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
