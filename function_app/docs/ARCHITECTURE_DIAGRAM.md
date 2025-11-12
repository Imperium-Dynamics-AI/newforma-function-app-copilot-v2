# Repository & Manager Refactoring Architecture

## Layer Structure (After Refactoring)

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Requests                            │
└──┬──────────────────────┬──────────────────────┬────────────┘
   │                      │                      │
   v                      v                      v
┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
│ TodoLists   │   │ TodoTasks    │   │ TodoSubtasks     │
│ Handler     │   │ Handler      │   │ Handler          │
│             │   │              │   │                  │
│ 4 methods   │   │ 7 methods    │   │ 4 methods        │
└──────┬──────┘   └──────┬───────┘   └────────┬─────────┘
       │                 │                    │
       v                 v                    v
┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
│ TodoLists   │   │ TodoTasks    │   │ TodoSubtasks     │
│ Manager     │   │ Manager      │   │ Manager          │
│             │   │              │   │                  │
│ Validation  │   │ Validation   │   │ Validation       │
│ Exception   │   │ Exception    │   │ Exception        │
│ wrapping    │   │ wrapping     │   │ wrapping         │
└──────┬──────┘   └──────┬───────┘   └────────┬─────────┘
       │                 │                    │
       v                 v                    v
┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
│ TodoLists   │   │ TodoTasks    │   │ TodoSubtasks     │
│ Repository  │   │ Repository   │   │ Repository       │
│             │   │              │   │                  │
│ Graph API   │   │ Graph API    │   │ Graph API        │
│ calls       │   │ calls        │   │ calls            │
└──────┬──────┘   └──────┬───────┘   └────────┬─────────┘
       │                 │                    │
       └─────────────────┼────────────────────┘
                         │
                         v
                    ┌──────────┐
                    │ GraphAPI │
                    │ Client   │
                    │          │
                    │ Auth     │
                    │ Manager  │
                    └────┬─────┘
                         │
                         v
                  Microsoft Graph API
```

## Dependency Injection Graph

```
┌─────────────────────────────────────┐
│     Dependency Injection Layer      │
└─────────────────────────────────────┘

get_auth_manager()
    └── returns: AuthManager

get_graph_client()
    └── depends on: AuthManager
    └── returns: GraphClient

┌─────────────────────────────────────┐
│         Repositories Layer          │
└─────────────────────────────────────┘

get_todo_lists_repository()
    └── depends on: GraphClient
    └── returns: TodoListsRepository

get_todo_tasks_repository()
    └── depends on: GraphClient
    └── returns: TodoTasksRepository

get_todo_subtasks_repository()
    └── depends on: GraphClient
    └── returns: TodoSubtasksRepository

┌─────────────────────────────────────┐
│         Managers Layer              │
└─────────────────────────────────────┘

get_todo_lists_manager()
    └── depends on: TodoListsRepository
    └── returns: TodoListsManager

get_todo_tasks_manager()
    └── depends on: TodoTasksRepository
    └── returns: TodoTasksManager

get_todo_subtasks_manager()
    └── depends on: TodoSubtasksRepository
    └── returns: TodoSubtasksManager

┌─────────────────────────────────────┐
│          Handlers Layer             │
└─────────────────────────────────────┘

get_todo_lists_handler()
    └── depends on: TodoListsManager
    └── returns: TodoListsHandler

get_todo_tasks_handler()
    └── depends on: TodoTasksManager
    └── returns: TodoTasksHandler

get_todo_subtasks_handler()
    └── depends on: TodoSubtasksManager
    └── returns: TodoSubtasksHandler
```

## Class Responsibility Matrix

```
┌─────────────────┬────────────────────┬─────────────────┬────────────────────┐
│ Component       │ Responsibility     │ LOC            │ Methods            │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoListsRepo   │ Graph API calls    │ 133            │ create_list        │
│                 │ for Lists          │                │ get_lists          │
│                 │                    │                │ edit_list          │
│                 │                    │                │ delete_list        │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoTasksRepo   │ Graph API calls    │ 218            │ create_task        │
│                 │ for Tasks          │                │ get_tasks          │
│                 │                    │                │ edit_task          │
│                 │                    │                │ update_task_status │
│                 │                    │                │ update_description │
│                 │                    │                │ update_duedate     │
│                 │                    │                │ delete_task        │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoSubtasksRe  │ Graph API calls    │ 139            │ create_subtask     │
│                 │ for Subtasks       │                │ get_subtasks       │
│                 │                    │                │ edit_subtask       │
│                 │                    │                │ delete_subtask     │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoListsMgr    │ Validation &       │ 127            │ create_list        │
│                 │ exception wrapping │                │ get_lists          │
│                 │ for Lists          │                │ edit_list          │
│                 │                    │                │ delete_list        │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoTasksMgr    │ Validation &       │ 189            │ create_task        │
│                 │ exception wrapping │                │ get_tasks          │
│                 │ for Tasks          │                │ edit_task          │
│                 │                    │                │ update_task_status │
│                 │                    │                │ update_description │
│                 │                    │                │ update_duedate     │
│                 │                    │                │ delete_task        │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoSubtasksMgr │ Validation &       │ 122            │ create_subtask     │
│                 │ exception wrapping │                │ get_subtasks       │
│                 │ for Subtasks       │                │ edit_subtask       │
│                 │                    │                │ delete_subtask     │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoListsHndlr  │ HTTP parsing       │ 145            │ create_list        │
│                 │ response formatting│                │ get_lists          │
│                 │ for Lists          │                │ edit_list          │
│                 │                    │                │ delete_list        │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoTasksHndlr  │ HTTP parsing       │ 229            │ create_task        │
│                 │ response formatting│                │ get_tasks          │
│                 │ for Tasks          │                │ edit_task          │
│                 │                    │                │ update_task_status │
│                 │                    │                │ update_description │
│                 │                    │                │ update_duedate     │
│                 │                    │                │ delete_task        │
├─────────────────┼────────────────────┼─────────────────┼────────────────────┤
│ TodoSubtasksHnd │ HTTP parsing       │ 148            │ create_subtask     │
│                 │ response formatting│                │ get_subtasks       │
│                 │ for Subtasks       │                │ edit_subtask       │
│                 │                    │                │ delete_subtask     │
└─────────────────┴────────────────────┴─────────────────┴────────────────────┘

TOTAL: ~1,450 lines of well-organized, focused code
```

## Data Flow Example: Create Task

```
1. HTTP Request
   POST /api/tasks
   {
     "user_email": "user@example.com",
     "list_id": "list-123",
     "title": "Complete project",
     "description": "Finish all features",
     "due_date": "2025-12-31"
   }

2. TodoTasksHandler.create_task()
   ├── Parse JSON → CreateTaskRequest
   ├── Validate using Pydantic
   ├── Log: "Creating task 'Complete project'..."
   └── Call: manager.create_task()

3. TodoTasksManager.create_task()
   ├── Validate title not empty
   ├── Log: "Creating task '%s'..." % title
   ├── Call: repository.create_task()
   └── Catch exceptions → wrap in TodoAPIError

4. TodoTasksRepository.create_task()
   ├── Validate title not empty
   ├── Build payload
   ├── POST to /users/{email}/todo/lists/{list_id}/tasks
   ├── Parse response
   ├── Log: "Successfully created task '%s'" % title
   └── Return: {task_id, title, status, ...}

5. Response handling in Manager
   ├── Return dict to handler

6. Response handling in Handler
   ├── Serialize to JSON
   ├── Log: "Task created successfully: task-456"
   └── Return: 201 Created with task data
```

## Error Flow Example

```
Error at Repository Level (Graph API fails)
    ↓
raise Exception("API error details")
    ↓
Manager catches Exception
    ├── Logs: "Error creating task: API error details"
    ├── Wraps in TodoAPIError with status_code
    └── Re-raises TodoAPIError
    ↓
Handler catches TodoAPIError
    ├── Logs: "API error creating task: API error details"
    ├── Calls: e.to_response() → {"error": "detail"}
    ├── Returns: 500 or appropriate status code
    └── JSON response sent to client

Client receives: {"error": "Internal server error"} with 500 status
```
