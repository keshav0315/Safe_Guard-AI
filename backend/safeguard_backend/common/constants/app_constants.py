# Application-wide constants

# Emergency event statuses
EMERGENCY_STATUS_ACTIVE = 'active'
EMERGENCY_STATUS_CANCELLED = 'cancelled'
EMERGENCY_STATUS_RESOLVED = 'resolved'
EMERGENCY_STATUS_ACKNOWLEDGED = 'acknowledged'

# Notification statuses
NOTIFICATION_STATUS_PENDING = 'pending'
NOTIFICATION_STATUS_SENT = 'sent'
NOTIFICATION_STATUS_DELIVERED = 'delivered'
NOTIFICATION_STATUS_FAILED = 'failed'
NOTIFICATION_STATUS_RETRYING = 'retrying'

# User roles
ROLE_USER = 'user'
ROLE_GUARDIAN = 'guardian'
ROLE_ADMIN = 'admin'

# Location sharing scopes
SHARING_SCOPE_PRIVATE = 'private'
SHARING_SCOPE_CONTACTS = 'contacts'
SHARING_SCOPE_PUBLIC_LINK = 'public_link'

# Max retries for notification
MAX_NOTIFICATION_RETRIES = 3

# Location snapshot expiry default (minutes)
DEFAULT_LOCATION_SHARE_EXPIRY_MINUTES = 60

# Idempotency key prefix
IDEMPOTENCY_KEY_PREFIX = 'user_'

# Rate limiting
SOS_RATE_LIMIT = '5/minute'
API_DEFAULT_RATE_LIMIT = '100/minute'
