# nCino Surfboard Checkout System

## Project Brief — AI-Assisted Development Hackathon

---

## EXECUTIVE SUMMARY

Build a multi-location surfboard checkout and inventory management system. This is a full-stack engineering challenge designed to teach effective Claude Code workflows for architecture, design, and implementation decisions.

**Objective:** Ship a working system by end of day using Claude Code as your primary development tool.

**Timeline:** 1 day (setup completed prior)

- Coding window: ~6-7 hours
- Presentations: ~7 minutes

---

## PROJECT OBJECTIVES

**Primary Goals:**

1. Become fluent with Claude Code workflow for building net-new projects
2. Apply enterprise software patterns (multi-tenancy, timezone handling, real-time state)
3. Make architecture and design decisions with Claude Code assistance
4. Ship a fully functional system
5. Articulate design patterns and reasoning

**Learning Outcomes:**

- How to use Claude Code effectively for API/service layer design
- Multi-tenancy data isolation patterns
- Timezone-aware business logic
- Real-time state management
- Concurrent operation handling
- How to iterate and refine code through Claude Code prompts

---

## FUNCTIONAL REQUIREMENTS

### User Checkout Flow

- View available surfboards at their location (real-time availability)
- Check out a board with auto-calculated return window (1 day or weekend)
- Return a board and update system status
- Report damage during return → marks board unavailable, triggers admin notification
- Cancel a checkout

### Reservation System

- Reserve a checked-out board (only after board's return date/time in user's timezone)
- View reservation queue for each board
- Receive notification when reserved board becomes available
- Cancel a reservation

### Admin Portal

- **Real-time Dashboard:** available boards, checked-out boards, all boards inventory
- **Checkout Schedule/Calendar:** visual representation of checkout timeline
- **Activity Log:** user, board, action, timestamp (complete audit trail)
- **Damage Queue:** boards flagged for repair with status tracking (New → In Repair → Replaced)
- **Reporting:**
  - Favorite boards (most checked out)
  - Usage per user
  - Usage per location
  - Usage trends
- **Location Management:** add/edit locations with timezone configuration
- **Role-Based Access:** admins manage only their assigned location

### Bonus Features (if time permits)

- 5-star board ratings with written reviews/notes
- Advanced reporting (seasonal trends, peak usage times, damage frequency by board)

---

## SYSTEM CONSTRAINTS

### Multi-Tenancy

- Users see only boards at their location
- Admins manage only their assigned location
- Data must be properly isolated (no cross-location leakage)

### Timezone Handling

- Checkout window (1 day vs. weekend) calculated based on location timezone
- Reservations unlock based on return date/time in user's timezone
- Real-time availability accounts for timezone differences
- All timestamps preserve timezone context

### Real-Time Requirements

- Dashboard updates reflect current board status without page refresh
- Availability calculations are live (not cached)
- Notifications trigger immediately when boards become available

---

## ACCEPTANCE CRITERIA

All items marked ✅ must be working for completion:

- ✅ User can checkout a board at their location
- ✅ User can return a board and update system status
- ✅ Real-time availability reflects current board status (Available/Damaged/In Repair)
- ✅ User can reserve a checked-out board only after return datetime (timezone-aware)
- ✅ Damage report on return blocks board from future checkouts
- ✅ Admin is notified when board is damaged
- ✅ Admin dashboard displays real-time data: available, checked-out, all boards
- ✅ Admin sees activity log with accurate timestamps and user actions
- ✅ Admin manages damage queue with status tracking (New → In Repair → Replaced)
- ✅ Admin can run reports: favorite boards, usage per user, usage per location
- ✅ Checkout window respects location timezone (1 day vs. weekend calculated correctly)
- ✅ Multi-tenancy enforced: users/admins only see their location's data
- ✅ System handles concurrent checkouts/reservations without data corruption
- ✅ User receives notification when their reservation becomes available

---

## TECH STACK

**You choose.** Select you want to learn.

**No preference for this hackathon.** The goal is learning Claude Code workflow, not tech stack mastery.

---

## JUDGING RUBRIC

### Functionality

### Architecture & Design

### Code Quality & Claude Code Workflow

---

## PRESENTATION REQUIREMENTS

**Format:** 7 minutes per person

- 4 minutes: Live demo (checkout → return → reservation → admin dashboard)
- 3 minutes: Design explanation (data model, multi-tenancy approach, timezone logic, why Claude Code was helpful)

**What to Cover:**

1. **Architecture Overview** — API design, service layer, database schema (why these choices?)
2. **Core Flow Demo** — checkout, return, damage report working end-to-end
3. **Reservation Logic** — show timezone-aware unlock in action
4. **Admin Portal** — dashboard, activity log, damage queue
5. **Claude Code Workflow** — how did you use Claude Code? What prompts were most effective? What did you iterate on?
6. **Lessons Learned** — what was harder than expected? What would you do differently?

---

## HOW TO USE CLAUDE CODE

Claude Code is your primary development tool. Use it to:

- **Architecture decisions** — ask Claude to design the API, database schema, service layer
- **Complex logic** — timezone calculations, multi-tenancy filtering, real-time state management
- **Code generation** — models, controllers, components, utility functions
- **Iteration** — refine generated code, ask Claude why certain patterns were chosen
- **Debugging** — explain errors, ask for optimization suggestions

**Best Practices:**

- **Be specific in prompts** — describe the problem, constraints, and expected behavior
- **Ask "why"** — understand design decisions, don't just copy code
- **Iterate** — first pass may not be perfect; refine and improve
- **Test as you go** — verify each feature works before moving to the next

---

**If you don't complete by end of day:**

1. Presentation is still required
2. Focus on what's working and why
3. Explain what didn't work and lessons learned
4. Partially working systems are acceptable; show what you've built

## QUESTIONS?

Ask before you start coding. Clarification on requirements is free. Assumptions you make in silence may cost you hours.

Good luck.
