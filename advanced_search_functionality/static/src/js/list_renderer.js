odoo.define('advanced_search_functionality.Listrenderer', function(require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var ListRenderer = require('web.ListRenderer');
    var _t = core._t;
    var odoo_advance_search_utils = require('advanced_search_functionality.utils');
    ListRenderer.include({
       /* _onKeyPress: function() {
            return
        },*/
        _hasContent: function() {
            return true;
        },
        _onKeyPress : function(e){
//            if (!this.editable) {
//            switch (e.which) {
//                case $.ui.keyCode.DOWN:
//                    $(e.currentTarget).next().find('input').focus();
//                    e.preventDefault();
//                    break;
//                case $.ui.keyCode.UP:
//                    $(e.currentTarget).prev().find('input').focus();
//                    e.preventDefault();
//                    break;
//                case $.ui.keyCode.ENTER:
//                    e.preventDefault();
//                    var id = $(e.currentTarget).data('id');
//                    if (id) {
//                        this.trigger_up('open_record', { id: id, target: e.target });
//                    }
//                    break;
//            }
//        }

        },
        _onKeyDown: function (e) {
//            if (!this.editable) {
//                switch (e.which) {
//                    case $.ui.keyCode.DOWN:
//                        $(e.currentTarget).next().find('input').focus();
//                        e.preventDefault();
//                        break;
//                    case $.ui.keyCode.UP:
//                        $(e.currentTarget).prev().find('input').focus();
//                        e.preventDefault();
//                        break;
//                    case $.ui.keyCode.ENTER:
//                        e.preventDefault();
//                        var id = $(e.currentTarget).data('id');
//                        if (id) {
//                            this.trigger_up('open_record', { id: id, target: e.target });
//                        }
//                        break;
//                }
//            }
        },
        _renderHeader: function(isGrouped) {
            var $thead = this._super(isGrouped);
            var self = this;
            if (self.def_column_val === undefined) {
                self.def_column_val = {}
            }
            if (this.getParent().hasSidebar) {
                var $tr2 = $("<tr class='advance_search_row'>").append(_.map(this.columns, function(column) {
                    var $td = $('<td>');
                    var field_name = column.attrs.name;
                    var field = self.state.fields[field_name];
//                    console.log('--------223233---',field_name,field);
                    if (!field || !field.searchable || (column.attrs.widget !== undefined && column.attrs.widget === 'handle')) {
                        return $td;
                    }
                    var field_value = self.def_column_val[field_name]
                    if (!field_value) {
                        field_value = ''
                    }
                    if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
                        var input_tag = "<input type='text' class='odoo_field_search_expan o_list_number' name='" + field_name + "' field_type='" + field.type + "' style='width:100%;'" + " value='" + field_value + "'>";
                        var $input = $(input_tag);
                    } else if (field.type === 'many2one') {
                        var $input1 = $('<input type="hidden"/>').attr('class', 'odoo_field_search_expan o_list_text');
                        $input1.attr('name', field_name);
                        $input1.attr('field_type', field.type);
                        $input1.attr('style', 'width:100%;');
                        $input1.attr('search_model', field.relation);
                        $input1.attr('placeholder', 'select');
                        if ($.isArray(field_value) && field_value.length === 2) {
                            $input1.attr('value', field_value[0]);
                            $input1.attr('title', field_value[1]);
                        } else {
                            $input1.attr('value', field_value);
                        }
                        var $input = $('<div/>').append($input1);
                        odoo_advance_search_utils.setAsRecordSelect($input1);
                    } else if (field.type === 'text' || field.type === 'char' || field.type === 'one2many' || field.type === 'many2many' || field.type === 'many2one') {
                        var input_tag = "<input type='text' class='odoo_field_search_expan o_list_text' name='" + field_name + "' field_type='" + field.type + "' style='width:100%;'" + " value='" + field_value + "'>";
                        var $input = $(input_tag);
                    } else if (field.type === 'boolean') {
                        var input_tag = "<select class='odoo_field_search_expan' name='" + field_name + "' field_type='" + field.type + "' style='width:100%;'" + ">";
                        var $input = $(input_tag);
                        $input[0].add($('<option>')[0])
                        field_value === 'true' ? $input[0].add($("<option selected=true value='true'>").text(_t("Yes"))[0]) : $input[0].add($("<option value='true'>").text(_t("Yes"))[0]);
                        field_value === 'false' ? $input[0].add($("<option selected=true value='false'>").text(_t("No"))[0]) : $input[0].add($("<option value='false'>").text(_t("No"))[0]);
                    } else if (field.type === 'date' || field.type === 'datetime') {
                        if (session.has_advance_search_group) {
                            var field_value_from = self.def_column_val[field_name + '_from']
                            var field_value_to = self.def_column_val[field_name + '_to']
                            if (!field_value_from) {
                                field_value_from = ''
                            }
                            if (!field_value_to) {
                                field_value_to = ''
                            }
                            var input_tag1 = "<div><input type='date' class='odoo_field_search_expan' name='" + field_name + "_from' field_type='" + field.type + "' ' style='float:left;width:100%;line-height: inherit;' value='" + field_value_from + "'></div>";
                            var input_tag2 = "<div><input type='date' class='odoo_field_search_expan' name='" + field_name + "_to' field_type='" + field.type + "' placeholder='To :' style='float:left;width:100%;line-height: inherit;margin-top:5px;display:none;' value='" + field_value_to + "'></div>";
                            var input_tag = input_tag1 + input_tag2;
                        } else {
                            var input_tag = "<input type='date' class='odoo_field_search_expan' name='" + field_name + "' field_type='" + field.type + "' style='float:left;width:100%;line-height: inherit;' value='" + field_value + "'>";
                        }
                        var $input = $(input_tag);
                    } else if (field.type === 'selection') {
                        var input_tag = "<select class='odoo_field_search_expan' name='" + field_name + "' field_type='" + field.type + "' style='width:100%;'>"
                        var $input = $(input_tag);
                        $input[0].add($('<option>')[0]);
                        $.each(field.selection, function(index) {
                            var key = field.selection[index][0];
                            var value = field.selection[index][1];
                            var selected = self.def_column_val[field_name] === key
                            if (selected) {
                                var option_tag = "<option selected='selected' value='" + key + "'>";
                                $input[0].add($(option_tag).text(value)[0]);
                            } else {
                                var option_tag = "<option value='" + key + "' >";
                                $input[0].add($(option_tag).text(value)[0]);
                            }
                        })
                    }
                    $td.append($input)
                    return $td;
                }));
                if (this.hasSelectors) {
                    $tr2.prepend($('<td>').append('<i class="fa fa-refresh ba_search_field_erase" style="display: block !important;" aria-hidden="true"></i>'));
                }
                if ($thead.find("th.o_list_row_number_header").length > 0) {
                    $tr2.prepend($('<td class="o_list_row_number_header">').html('&nbsp;'));
                }
                $thead.append($tr2);
            }
            return $thead;
        },
    });
});