'use strict';
import { EventCalendar} from "./calendar.js";
import {EventList} from "./event_list.js";

let calendar_container = document.getElementById("cal-container");
let calendar = new EventCalendar(calendar_container);

let event_list_container;