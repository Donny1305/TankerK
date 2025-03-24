[app]
# Author: Marian Neff

title = Tankerkoenig
package.name = Tankerkoenig
package.domain = gsog.eigeneDomain

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy,kivymd,kivy_garden.mapview,requests,geopy,geocoder,ratelim,decorator,click,future,six

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.permissions = INTERNET

icon.filename = %(source.dir)s/images/tankericon.png

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = main
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2
