"""Constants and labels for the application"""

# Board Status
BOARD_STATUS_AVAILABLE = 'available'
BOARD_STATUS_CHECKED_OUT = 'checked_out'
BOARD_STATUS_DAMAGED = 'damaged'
BOARD_STATUS_IN_REPAIR = 'in_repair'
BOARD_STATUS_REPLACED = 'replaced'

# Board Condition
BOARD_CONDITION_EXCELLENT = 'excellent'
BOARD_CONDITION_GOOD = 'good'
BOARD_CONDITION_FAIR = 'fair'

# Checkout Status
CHECKOUT_STATUS_ACTIVE = 'active'
CHECKOUT_STATUS_RETURNED = 'returned'
CHECKOUT_STATUS_CANCELLED = 'cancelled'

# Reservation Status
RESERVATION_STATUS_PENDING = 'pending'
RESERVATION_STATUS_AVAILABLE = 'available'
RESERVATION_STATUS_FULFILLED = 'fulfilled'
RESERVATION_STATUS_CANCELLED = 'cancelled'

# Damage Report Status
DAMAGE_STATUS_NEW = 'new'
DAMAGE_STATUS_IN_REPAIR = 'in_repair'
DAMAGE_STATUS_REPLACED = 'replaced'

# Damage Severity
DAMAGE_SEVERITY_MINOR = 'minor'
DAMAGE_SEVERITY_MODERATE = 'moderate'
DAMAGE_SEVERITY_SEVERE = 'severe'

# User Roles
USER_ROLE_USER = 'user'
USER_ROLE_ADMIN = 'admin'

# Activity Log Action Types
ACTION_CHECKOUT = 'checkout'
ACTION_RETURN = 'return'
ACTION_RESERVATION = 'reservation'
ACTION_DAMAGE_REPORT = 'damage_report'
ACTION_CANCEL_CHECKOUT = 'cancel_checkout'
ACTION_CANCEL_RESERVATION = 'cancel_reservation'
ACTION_BOARD_STATUS_CHANGE = 'board_status_change'
ACTION_DAMAGE_STATUS_CHANGE = 'damage_status_change'

# Flash Messages (with personality!)
MSG_LOGIN_SUCCESS = 'Welcome back! Ready to catch some waves? 🏄‍♂️'
MSG_LOGIN_FAILED = 'Oops! That login wiped out. Let\'s try again!'
MSG_REGISTRATION_SUCCESS = 'Welcome to the crew! Time to make some memories! 🎉'
MSG_REGISTRATION_FAILED = 'Registration hit a snag. Don\'t worry, we\'ll get you in!'
MSG_LOGOUT_SUCCESS = 'See you next time! Keep the stoke alive! 🏄‍♂️'
MSG_CHECKOUT_SUCCESS = 'Board checked out! Time to make some memories (and probably some wipeouts)! 🎉'
MSG_CHECKOUT_FAILED = 'That checkout wiped out. But don\'t worry - there are more boards in the sea!'
MSG_RETURN_SUCCESS = 'Board returned! Hope you had fun out there! 🏄‍♂️'
MSG_RETURN_FAILED = 'Return hit a snag. Let\'s try again!'
MSG_CANCEL_SUCCESS = 'Cancelled! No worries - there\'s always next time!'
MSG_CANCEL_FAILED = 'Cancellation wiped out. Let\'s try again!'
MSG_RESERVATION_SUCCESS = 'Reservation set! Your next adventure is locked in! 🎉'
MSG_RESERVATION_FAILED = 'Reservation got swept away. No worries, try again!'
MSG_DAMAGE_REPORTED = 'Thanks for reporting! We\'ll get that board some TLC.'
MSG_ACCESS_DENIED = 'Whoa there! That area\'s for admins only.'
MSG_NOT_FOUND = 'Hmm, that wave (or page) seems to have passed. Try another!'
MSG_INTERNAL_ERROR = 'Oops! Something wiped out on our end. We\'re on it!'

# Error Messages
ERROR_BOARD_NOT_FOUND = 'Board not found'
ERROR_BOARD_NOT_AVAILABLE = 'Board is not available'
ERROR_BOARD_ALREADY_CHECKED_OUT = 'Board is already checked out'
ERROR_BOARD_NOT_AT_LOCATION = 'Board not at user\'s location'
ERROR_CHECKOUT_NOT_FOUND = 'Checkout not found'
ERROR_CHECKOUT_NOT_ACTIVE = 'Checkout is not active'
ERROR_CHECKOUT_NOT_BELONGS = 'Checkout does not belong to user'
ERROR_RESERVATION_NOT_FOUND = 'Reservation not found'
ERROR_RESERVATION_NOT_BELONGS = 'Reservation does not belong to user'
ERROR_RESERVATION_EXISTS = 'Reservation already exists for this checkout'
ERROR_RESERVATION_NOT_AVAILABLE = 'Reservation is not available'
ERROR_RESERVATION_CANNOT_CANCEL = 'Reservation cannot be cancelled'
ERROR_RETURN_TIME_PASSED = 'Return time has already passed'
ERROR_USER_NOT_FOUND = 'User not found in database'
ERROR_INVALID_CREDENTIALS = 'Invalid credentials'
ERROR_SUPABASE_NOT_CONFIGURED = 'Supabase not configured'
ERROR_DATABASE_NOT_CONFIGURED = 'Database configuration missing. Please set DATABASE_URL or individual DB parameters (user, password, host, port, dbname)'

# UI Labels
LABEL_DASHBOARD = 'Dashboard'
LABEL_BOARDS = 'Boards'
LABEL_MY_CHECKOUTS = 'My Checkouts'
LABEL_RESERVATIONS = 'Reservations'
LABEL_ADMIN = 'Admin'
LABEL_INVENTORY = 'Inventory'
LABEL_DAMAGE_QUEUE = 'Damage Queue'
LABEL_ACTIVITY_LOG = 'Activity Log'
LABEL_REPORTS = 'Reports'
LABEL_LOGIN = 'Login'
LABEL_LOGOUT = 'Logout'
LABEL_REGISTER = 'Register'
LABEL_AVAILABLE_BOARDS = 'Available Boards'
LABEL_ACTIVE_CHECKOUTS = 'My Active Checkouts'
LABEL_MY_RESERVATIONS = 'My Reservations'
LABEL_CHECKOUT = 'Checkout'
LABEL_RETURN = 'Return'
LABEL_CANCEL = 'Cancel'
LABEL_RESERVE = 'Reserve'
LABEL_FULFILL = 'Fulfill Reservation'
LABEL_NO_BOARDS_AVAILABLE = 'No boards available at this time.'
LABEL_NO_ACTIVE_CHECKOUTS = 'You have no active checkouts.'
LABEL_NO_RESERVATIONS = 'You have no reservations.'

# Status Display Labels
LABEL_STATUS_AVAILABLE = 'Available'
LABEL_STATUS_CHECKED_OUT = 'Checked Out'
LABEL_STATUS_DAMAGED = 'Damaged'
LABEL_STATUS_IN_REPAIR = 'In Repair'
LABEL_STATUS_REPLACED = 'Replaced'
LABEL_STATUS_ACTIVE = 'Active'
LABEL_STATUS_RETURNED = 'Returned'
LABEL_STATUS_CANCELLED = 'Cancelled'
LABEL_STATUS_PENDING = 'Pending'
LABEL_STATUS_FULFILLED = 'Fulfilled'

# Severity Display Labels
LABEL_SEVERITY_MINOR = 'Minor'
LABEL_SEVERITY_MODERATE = 'Moderate'
LABEL_SEVERITY_SEVERE = 'Severe'

# Condition Display Labels
LABEL_CONDITION_EXCELLENT = 'Excellent'
LABEL_CONDITION_GOOD = 'Good'
LABEL_CONDITION_FAIR = 'Fair'
