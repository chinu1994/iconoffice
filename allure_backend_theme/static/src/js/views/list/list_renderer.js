odoo.define('allure_backend_theme.ListRenderer', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');
    var DocumentViewer = require('mail.DocumentViewer');
    var core = require('web.core');
    var QWeb = core.qweb;

    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click .o_attachment_view': '_onAttachmentView',
            'click tbody tr td': '_onRowClicked',
            'click tbody tr td .attachment-counter': '_onRowClicked',
            'click tbody tr td .o_attachment_download': '_onAttachmentClick',
        }),
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.resIDs = state.res_ids;
            this.resModel = state.model;
            this.attachmentsData = state.attachmentsData || [];
            this.nbAttahments = state.nbAttahments || [];
            this.displayDensity = state.displayDensity;
            this.records = {};
        },
        updateState: function (state) {
            this.state = state;
            this.attachmentsData = state.attachmentsData || [];
            this.nbAttahments = state.nbAttahments || [];
            this.displayDensity = state.displayDensity;
            return this._super.apply(this, arguments);
        },
        _renderRow: function (record) {
            var self = this;
            var $tr = this._super.apply(this, arguments);
            if (self.displayDensity && self.displayDensity.display_density !== 'default') {
                $tr.addClass('o_' + self.displayDensity.display_density);
            }
            _.each(this.attachmentsData, function (values) {
                if (values[record.res_id]) {
                    var $attech = $('<td/>', {class: 'o_attachment'});
                    if (self.displayDensity) {
                        $tr.addClass('o_' + self.displayDensity.display_density);
                    }
                    $tr.data('res_id', record.res_id);
                    $tr.find('td:nth-child(2)').append($attech);
                    $tr.find('.o_attachment').append(QWeb.render('ListView.Attachment', {
                        values: values[record.res_id],
                    }));
                }
            });
            _.each(this.nbAttahments, function (attach) {
                if (attach[record.res_id] && attach[record.res_id] > 3) {
                    $tr.find('.o_attachment').append('<div class="attachment-counter">+' + (attach[record.res_id] - 3) + '</div>')
                }
            });
            return $tr;
        },
        _onAttachmentView: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            var activeAttachmentID = $(ev.currentTarget).data('id');
            var res_id = $(ev.currentTarget).closest('tr').data('res_id');
            if (activeAttachmentID && res_id) {
                var attachmentData = _.compact(_.map(this.attachmentsData, function (record) {
                    return record[res_id];
                }));
                if (attachmentData) {
                    var attachmentViewer = new DocumentViewer(this, attachmentData[0], activeAttachmentID);
                    attachmentViewer.appendTo($('body'));
                }
            }
        },
        _onAttachmentClick: function (ev) {
            ev.stopPropagation();
        }
    });
});