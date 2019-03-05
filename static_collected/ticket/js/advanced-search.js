var DatatablesSearchOptionsAdvancedSearch = function () {
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    $.fn.dataTable.Api.register("column().title()", function () {
        return $(this.header()).text().trim()
    });
    return {
        init: function () {
            var a;
            a = $("#m_table_1").DataTable({
                responsive: !0,
                dom: "<'row'<'col-sm-12'tr>>\n\t\t\t<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>",
                lengthMenu: [5, 10, 25, 50],
                pageLength: 10,
                language: {lengthMenu: "Display _MENU_"},
                searchDelay: 500,
                processing: !0,
                serverSide: !0,
                ajax: {
                    url: "/",
                    type: "POST",
                    beforeSend: function (xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    },
                    dataSrc: 'fields',
                    data: {columnsDef: ["code", "name", "phone_number", "created_date", "final_amount", "paid_amount", "status", "percent", "actions"]}
                },
                columns: [{data: "code"}, {data: "name"}, {data: "phone_number"}, {data: "created_date"}, {data: "final_amount"}, {data: "paid_amount"}, {data: "status"}, {data: "percent"}, {data: "actions"}],
                initComplete: function () {
                    this.api().columns().every(function () {
                        switch (this.title()) {
                            case"وضعیت فاکتور":
                                var a = {
                                    1: {title: "پرداخت شده", class: "m-badge--success"},
                                    2: {title: "نیمه پرداخت شده", class: " m-badge--warning"},
                                    3: {title: "پرداخت نشده", class: " m-badge--danger"}
                                };
                                this.data().unique().sort().each(function (t, e) {
                                    $('.m-input[data-col-index="5"]').append('<option value="' + t + '">' + a[t].title + "</option>")
                                });
                                break;
                        }
                    })
                },
                columnDefs: [{
                    targets: -1, title: "actions", orderable: !1, render: function (a, t, e, n) {
                        return  '<a href="/update-factor/?code=' + e.action + '" class="m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="View"> <i class="la la-edit"></i> </a>'
                    }
                }, {
                    targets: 6, render: function (a, t, e, n) {
                        var i = {
                            1: {title: "پرداخت شده", class: "m-badge--success"},
                            2: {title: "نیمه پرداخت شده", class: " m-badge--warning"},
                            3: {title: "پرداخت نشده", class: " m-badge--danger"}
                        };
                        return void 0 === i[a] ? a : '<span class="m-badge ' + i[a].class + ' m-badge--wide">' + i[a].title + "</span>"
                    }
                }]
            }), $("#m_search").on("click", function (t) {
                t.preventDefault();
                var e = {};
                $(".m-input").each(function () {
                    var a = $(this).data("col-index");
                    e[a] ? e[a] += "|" + $(this).val() : e[a] = $(this).val()
                }), $.each(e, function (t, e) {
                    a.column(t).search(e || "", !1, !1)
                }), a.table().draw()
            }), $("#m_reset").on("click", function (t) {
                t.preventDefault(), $(".m-input").each(function () {
                    $(this).val(""), a.column($(this).data("col-index")).search("", !1, !1)
                }), a.table().draw()
            }), $("#m_datepicker").datepicker({
                todayHighlight: !0,
                templates: {
                    leftArrow: '<i class="la la-angle-left"></i>',
                    rightArrow: '<i class="la la-angle-right"></i>'
                }
            })
        }
    }
}();
jQuery(document).ready(function () {
    DatatablesSearchOptionsAdvancedSearch.init()
});