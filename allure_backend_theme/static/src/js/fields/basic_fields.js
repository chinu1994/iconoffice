odoo.define('allure_backend_theme.basic_fields', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');

    basic_fields.UrlWidget.include({
        _renderBeforeButton: function () {
            return $('<button>', {
                type: 'button',
                class: 'o_url_globe fa fa-globe btn btn-link'
            })
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            if (this.attrs.widget === 'url') {
                this.$el = $('<div>', {
                    class: 'o_url_block'
                }).html(this.$el.add(this._renderBeforeButton()));
            }
            return def;
        }
    });

    basic_fields.FieldEmail.include({
        _renderBeforeButton: function () {
            return $('<button>', {
                type: 'button',
                class: 'o_email_envelope fa fa-envelope-open btn btn-link'
            })
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            if (this.attrs.widget === 'email') {
                this.$el = $('<div>', {
                    class: 'o_email_block'
                }).html(this.$el.add(this._renderBeforeButton()));
            }
            return def;
        },
    });

    basic_fields.FieldPhone.include({
        _renderBeforeButton: function () {
            return $('<button>', {
                type: 'button',
                class: 'o_phone_phone fa fa-phone btn btn-link'
            })
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            if (this.attrs.widget === 'phone') {
                this.$el = $('<div>', {
                    class: 'o_phone_block'
                }).html(this.$el.add(this._renderBeforeButton()));
            }
            return def;
        },
    });

    basic_fields.FieldDate.include({
        _renderBeforeButton: function () {
            return $('<button>', {
                type: 'button',
                class: 'o_date_calender fa fa-calendar btn btn-link'
            })
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            if (this.field.type === 'date') {
                this.$el = $('<div>', {
                    class: 'o_date_block'
                }).html(this.$el.add(this._renderBeforeButton()));
            }
            return def;
        },
    });

    basic_fields.FieldDateTime.include({
        _renderBeforeButton: function () {
            return $('<button>', {
                type: 'button',
                class: 'o_date_calender fa fa-calendar btn btn-link'
            })
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            if (this.field.type === 'datetime') {
                this.$el = $('<div>', {
                    class: 'o_date_time_block'
                }).html(this.$el.add(this._renderBeforeButton()));
            }
            return def;
        },
    });
});
