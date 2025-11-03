import azure.functions as func
from create_event import createEvent
from event_manipulation import (
    deleteEvent,
    editEventSubject,
    editEventDescription,
    editEventDateTime,
    getEventsByDate,
    addAttendeesToEvent,
    modifyAttendees,
)
from recurring_weekly_event import weeklyRecurringEvents
from recurring_monthly_absolute_event import absoluteMonthlyRecurringEvents
from recurring_yearly_absolute_event import absoluteYearlyRecurringEvents
from recurring_daily_event import dailyRecurringEvents

from fetch_todo_items import get_todo_lists, get_task_titles_in_list, get_subtasks
from create_todo_items import createTodoList, createTodoTask, create_subtask
from delete_todo_items import delete_todo_list, delete_task, delete_subtask
from edit_todo_items import (
    edit_todo_list_name,
    edit_task_title,
    edit_subtask_title,
    update_task_status,
    update_task_description,
    update_duedate,
)

from birthday_reminder import EventCreator
from birthday_reminder_with_email import EventCreatorWithEmail


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="CreateEvent")
def createevent(req: func.HttpRequest) -> func.HttpResponse:
    return createEvent(req)


@app.route(route="getAllEvents")
def getAllEventsByDate(req: func.HttpRequest) -> func.HttpResponse:
    return getEventsByDate(req)


@app.route(route="deleteEvent")
def deleteEventById(req: func.HttpRequest) -> func.HttpResponse:
    return deleteEvent(req)


@app.route(route="editEventSubject")
def editEventSubjectById(req: func.HttpRequest) -> func.HttpResponse:
    return editEventSubject(req)


@app.route(route="editEventDescription")
def editEventDescriptionById(req: func.HttpRequest) -> func.HttpResponse:
    return editEventDescription(req)


@app.route(route="editEventDateTime")
def editEventDateTimeById(req: func.HttpRequest) -> func.HttpResponse:
    return editEventDateTime(req)


@app.route(route="weeklyEvents")
def weeklyEvents(req: func.HttpRequest) -> func.HttpResponse:
    return weeklyRecurringEvents(req)


@app.route(route="absoluteMonthlyEvents")
def absoluteMonthlyEvents(req: func.HttpRequest) -> func.HttpResponse:
    return absoluteMonthlyRecurringEvents(req)


@app.route(route="absoluteYearlyEvents")
def absoluteYearlyEvents(req: func.HttpRequest) -> func.HttpResponse:
    return absoluteYearlyRecurringEvents(req)


@app.route(route="dailyEvents")
def dailyEvents(req: func.HttpRequest) -> func.HttpResponse:
    return dailyRecurringEvents(req)


@app.route(route="getAllLists")
def getAllLists(req: func.HttpRequest) -> func.HttpResponse:
    return get_todo_lists(req)


@app.route(route="getAllTasks")
def getAllTasks(req: func.HttpRequest) -> func.HttpResponse:
    return get_task_titles_in_list(req)


@app.route(route="getAllSubtasks")
def getAllSubtasks(req: func.HttpRequest) -> func.HttpResponse:
    return get_subtasks(req)


@app.route(route="createList")
def createList(req: func.HttpRequest) -> func.HttpResponse:
    return createTodoList(req)


@app.route(route="createTask")
def createTask(req: func.HttpRequest) -> func.HttpResponse:
    return createTodoTask(req)


@app.route(route="createSubtasks")
def createSubtasks(req: func.HttpRequest) -> func.HttpResponse:
    return create_subtask(req)


@app.route(route="deleteLists")
def deleteLists(req: func.HttpRequest) -> func.HttpResponse:
    return delete_todo_list(req)


@app.route(route="deleteTasks")
def deleteTasks(req: func.HttpRequest) -> func.HttpResponse:
    return delete_task(req)


@app.route(route="deleteSubtasks")
def deleteSubtasks(req: func.HttpRequest) -> func.HttpResponse:
    return delete_subtask(req)


@app.route(route="editListName")
def editListName(req: func.HttpRequest) -> func.HttpResponse:
    return edit_todo_list_name(req)


@app.route(route="editTaskName")
def editTaskName(req: func.HttpRequest) -> func.HttpResponse:
    return edit_task_title(req)


@app.route(route="editSubtaskName")
def editSubtaskName(req: func.HttpRequest) -> func.HttpResponse:
    return edit_subtask_title(req)


@app.route(route="updateTaskStatus")
def updateTaskStatus(req: func.HttpRequest) -> func.HttpResponse:
    return update_task_status(req)


@app.route(route="updateTaskDescription")
def updateTaskDescription(req: func.HttpRequest) -> func.HttpResponse:
    return update_task_description(req)


@app.route(route="addAttendee")
def addAttendee(req: func.HttpRequest) -> func.HttpResponse:
    return addAttendeesToEvent(req)


@app.route(route="modifyAttendees")
def modifyAttendeesinEvent(req: func.HttpRequest) -> func.HttpResponse:
    return modifyAttendees(req)


@app.route(route="updateDueDate")
def updateDueDate(req: func.HttpRequest) -> func.HttpResponse:
    return update_duedate(req)


@app.route(route="birthday_reminder")
def birthDay(req: func.HttpRequest) -> func.HttpResponse:
    return EventCreator(req)


@app.route(route="birthday_reminder_with_email")
def birthDayWithEmail(req: func.HttpRequest) -> func.HttpResponse:
    return EventCreatorWithEmail(req)
