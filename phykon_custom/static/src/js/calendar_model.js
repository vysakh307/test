odoo.define('Phykon_custom.SampleFramework', function (require) {
"use strict";

var AbstractModel = require('web.AbstractModel'); 


function dateToServer (date) {
    return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
}

return AbstractModel.extend({
    init: function () {
        this._super.apply(this, arguments);
        this.end_date = null;
        var week_start = _t.database.parameters.week_start;
        // calendar uses index 0 for Sunday but Odoo stores it as 7
        this.week_start = week_start !== undefined && week_start !== false ? week_start % 7 : moment().startOf('week').day();
        this.week_stop = this.week_start + 6;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Transform fullcalendar event object to OpenERP Data object
     */
    calendarEventToRecord: function (event) {
        // Normalize event_end without changing fullcalendars event.
        var data = {'name': event.title};
        var start = event.start.clone();
        var end = event.end && event.end.clone();


        var isDateEvent = this.fields[this.mapping.date_start].type === 'date';
        // An "allDay" event without the "all_day" option is not considered
        // as a 24h day. It's just a part of the day (by default: 7h-19h).
        if (event.allDay) {
            if (!this.mapping.all_day && !isDateEvent) {
                if (event.r_start) {
                    start.hours(event.r_start.hours())
                         .minutes(event.r_start.minutes())
                         .seconds(event.r_start.seconds())
                         .utc();
                    end.hours(event.r_end.hours())
                       .minutes(event.r_end.minutes())
                       .seconds(event.r_end.seconds())
                       .utc();
                } else {
                    // default hours in the user's timezone
                    start.hours(7);
                    end.hours(19);
                }
                start.add(-this.getSession().getTZOffset(start), 'minutes');
                end.add(-this.getSession().getTZOffset(end), 'minutes');
            }
        } else {
            start.add(-this.getSession().getTZOffset(start), 'minutes');
            end.add(-this.getSession().getTZOffset(end), 'minutes');
        }

    },
    /**
     * @param {Object} filter
     * @returns {boolean}
     */
   
});
});