"use strict";(function(){if(jQuery&&jQuery.fn&&jQuery.fn.select2&&jQuery.fn.select2.amd)var a=jQuery.fn.select2.amd;return a.define("select2/i18n/ru",[],function(){function a(a,b,c,d){return 5>a%10&&0<a%10&&5>a%100||20<a%100?1<a%10?c:b:d}return{errorLoading:function errorLoading(){return"\u041D\u0435\u0432\u043E\u0437\u043C\u043E\u0436\u043D\u043E \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u044B"},inputTooLong:function inputTooLong(b){var c=b.input.length-b.maximum,d="\u041F\u043E\u0436\u0430\u043B\u0443\u0439\u0441\u0442\u0430, \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u043D\u0430 "+c+" \u0441\u0438\u043C\u0432\u043E\u043B";return d+=a(c,"","a","\u043E\u0432"),d+=" \u043C\u0435\u043D\u044C\u0448\u0435",d},inputTooShort:function inputTooShort(b){var c=b.minimum-b.input.length,d="\u041F\u043E\u0436\u0430\u043B\u0443\u0439\u0441\u0442\u0430, \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u0435\u0449\u0435 \u0445\u043E\u0442\u044F \u0431\u044B "+c+" \u0441\u0438\u043C\u0432\u043E\u043B";return d+=a(c,"","a","\u043E\u0432"),d},loadingMore:function loadingMore(){return"\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u0434\u0430\u043D\u043D\u044B\u0445\u2026"},maximumSelected:function maximumSelected(b){var c="\u0412\u044B \u043C\u043E\u0436\u0435\u0442\u0435 \u0432\u044B\u0431\u0440\u0430\u0442\u044C \u043D\u0435 \u0431\u043E\u043B\u0435\u0435 "+b.maximum+" \u044D\u043B\u0435\u043C\u0435\u043D\u0442";return c+=a(b.maximum,"","a","\u043E\u0432"),c},noResults:function noResults(){return"\u0421\u043E\u0432\u043F\u0430\u0434\u0435\u043D\u0438\u0439 \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u043E"},searching:function searching(){return"\u041F\u043E\u0438\u0441\u043A\u2026"}}}),{define:a.define,require:a.require}})();

//# sourceMappingURL=ru-compiled.js.map