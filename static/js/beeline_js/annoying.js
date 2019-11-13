window.hd_annoying = (function() {
    'use strict';

    var hd_annoying = {};

    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match;
        });
    };

    Array.prototype.extend = function(array) {
        var self = this;
        array.forEach(function(val) {
            self.push(val);
        });
    };

    hd_annoying.getHDApiErrors = function (response) {
        var data = {
            response: response,
            errors: []
        };
        if (response.data && response.data.validation_errors) {
            for (var field in response.data.validation_errors) {
                if (response.data.validation_errors.hasOwnProperty(field)) {
                    var value = response.data.validation_errors[field];
                    if (Array.isArray(value)) {
                        value.forEach(function (value) {
                            data.errors.push(value);
                        });
                    } else {
                        data.errors.push(value);
                    }
                }
            }
        }
        if (!data.errors.length) {
            data.errors.push('Системная ошибка, обратитесь к администратору!');
        }
        return data;
    };

    return hd_annoying;
})();
