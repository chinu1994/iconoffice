odoo.define('allure_backend_theme.settings', function (require) {
    "use strict";

    var BaseSettingRenderer = require('base.settings');

    BaseSettingRenderer.Renderer.include({
        init: function () {
            this._super.apply(this, arguments);
            this.meniIcon = true;
        },
        willStart: function () {
            var self = this;
            return this._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['base_menu_icon'],
            }).then(function (result) {
                self.meniIcon = result;
            });
        },
        fileExists: function(filename) {
            filename = filename.trim();
            var response = jQuery.ajax({
                url: filename,
                type: 'HEAD',
                async: false
            }).status;
            return (response == "200");
        },
        _getAppIconUrl: function (module) {
            var path;
            var custom_icon_path = '';
            if(this.meniIcon === 'base_icon'){
                custom_icon_path = "/base/static/description/";
                path = "/"+module+"/static/description/icon.png";
            }
            else if(this.meniIcon === '2d_icon'){
                custom_icon_path = '/allure_backend_theme/static/src/img/menu_2d/';
                if(this.fileExists(custom_icon_path + module+'.png')){
                    path= custom_icon_path + module+".png"
                }else{
                    path = custom_icon_path +"/custom.png";
                    if(this.fileExists("/"+module+"/static/description/icon.png")){
                        path = "/"+module+"/static/description/icon.png";
                    }
                }
            }
            else if(this.meniIcon === '3d_icon'){
                custom_icon_path = '/allure_backend_theme/static/src/img/menu/';
                if(this.fileExists(custom_icon_path + module+'.png')){
                    path= custom_icon_path + module+".png"
                }else{
                    path = custom_icon_path +"/custom.png";
                    if(this.fileExists("/"+module+"/static/description/icon.png")){
                        path = "/"+module+"/static/description/icon.png";
                    }
                }
            }
            return module === "general_settings" ? custom_icon_path + "/settings.png" : path;
        },
    });
});