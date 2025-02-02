# -*- coding: UTF-8 -*-
# /*
#  *      Copyright (C) 2013 Libor Zoubek + jondas
#  *
#  *
#  *  This Program is free software; you can redistribute it and/or modify
#  *  it under the terms of the GNU General Public License as published by
#  *  the Free Software Foundation; either version 2, or (at your option)
#  *  any later version.
#  *
#  *  This Program is distributed in the hope that it will be useful,
#  *  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  *  GNU General Public License for more details.
#  *
#  *  You should have received a copy of the GNU General Public License
#  *  along with this program; see the file COPYING.  If not, write to
#  *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  *  http://www.gnu.org/copyleft/gpl.html
#  *
#  */

import xbmcaddon
from resources.lib import xbmcutil
from resources.lib.sosac import SosacContentProvider
from resources.lib.sutils import XBMCSosac
from resources.lib import util

__scriptid__ = 'plugin.video.sosac.ph'
__scriptname__ = 'sosac.ph'
__addon__ = xbmcaddon.Addon(__scriptid__)
__language__ = __addon__.getLocalizedString
__set__ = __addon__.getSetting

settings = {'downloads': __set__('downloads'), 'quality': __set__(
    'quality'), 'subs': __set__('subs') == 'true', 'lang': __set__('language')}

reverse_eps = __set__('order-episodes') == '0'
force_czech = __set__('force-czech') == 'true'
order_recently_by = __set__('order-recently-by')

util.info("URL: " + sys.argv[2])
params = util.params()
if params == {}:
    xbmcutil.init_usage_reporting(__scriptid__)

util.info("Running sosac provider with params: " + str(params))

sosac = SosacContentProvider(reverse_eps=reverse_eps, force_czech=force_czech,
                             order_recently_by=order_recently_by)
sosac.streamujtv_user = __set__('streamujtv_user')
sosac.streamujtv_pass = __set__('streamujtv_pass')
sosac.streamujtv_location = __set__('streamujtv_location')

XBMCSosac(sosac, settings, __addon__).run(params)
