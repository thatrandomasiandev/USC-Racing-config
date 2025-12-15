# USC Shibboleth Authentication Setup

## Overview

This application uses USC Shibboleth Service Provider (SP) for authentication with USC NetID login.

## Architecture

### Components

1. **Shibboleth Service Provider (SP)**: Installed at web server level (Apache/Nginx)
2. **FastAPI Backend**: Reads Shibboleth attributes from headers/environment
3. **Frontend**: Displays auth status and login/logout links

### Authentication Flow

1. User accesses protected resource
2. Shibboleth SP intercepts request
3. If not authenticated → redirects to USC IdP login
4. User logs in with USC NetID
5. USC IdP redirects back with SAML assertion
6. Shibboleth SP validates and sets headers/environment variables
7. FastAPI reads attributes and creates session
8. User is authenticated

## Server Setup

### 1. Install Shibboleth SP

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libapache2-mod-shib2  # For Apache
# OR
sudo apt-get install nginx libnginx-mod-http-shibboleth  # For Nginx
```

**On RHEL/CentOS:**
```bash
sudo yum install shibboleth
```

### 2. Configure Shibboleth SP

Edit `/etc/shibboleth/shibboleth2.xml`:

```xml
<ApplicationDefaults entityID="https://your-domain.usc.edu/shibboleth"
                     REMOTE_USER="uid"
                     signing="false"
                     encryption="false">
    
    <Sessions lifetime="28800" timeout="3600" 
              checkAddress="false" handlerURL="/Shibboleth.sso"
              handlerSSL="true">
        
        <Handler type="MetadataGenerator" Location="/Metadata" 
                 signing="false"/>
        <Handler type="Status" Location="/Status" 
                 acl="127.0.0.1 ::1"/>
        <Handler type="Session" Location="/Session" 
                 showAttributeValues="false"/>
        <Handler type="DiscoveryFeed" Location="/DiscoFeed"/>
    </Sessions>
    
    <MetadataProvider type="XML" 
                      uri="https://idp.usc.edu/idp/shibboleth"
                      backingFilePath="usc-idp-metadata.xml"
                      reloadInterval="7200">
    </MetadataProvider>
    
    <AttributeExtractor type="XML" 
                        validate="true"
                        path="attribute-map.xml"/>
    
    <AttributeResolver type="Query" 
                      subjectMatch="true"/>
    
    <AttributeFilter type="XML" 
                     validate="true"
                     path="attribute-policy.xml"/>
    
    <CredentialResolver type="File" 
                        key="sp-key.pem"
                        certificate="sp-cert.pem"/>
</ApplicationDefaults>
```

### 3. Configure Apache

Edit Apache config (e.g., `/etc/apache2/sites-available/usc-racing.conf`):

```apache
<VirtualHost *:443>
    ServerName your-domain.usc.edu
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    # Shibboleth configuration
    <Location />
        AuthType shibboleth
        ShibRequestSetting requireSession 1
        Require valid-user
    </Location>
    
    # Proxy to FastAPI backend
    ProxyPass /api http://localhost:8000/api
    ProxyPassReverse /api http://localhost:8000/api
    
    ProxyPass /ws ws://localhost:8000/ws
    ProxyPassReverse /ws ws://localhost:8000/ws
    
    # Pass Shibboleth headers to backend
    RequestHeader set X-Shib-Session-ID %{Shib-Session-ID}e
    RequestHeader set X-Shib-uid %{uid}e
    RequestHeader set X-Shib-mail %{mail}e
    RequestHeader set X-Shib-givenName %{givenName}e
    RequestHeader set X-Shib-sn %{sn}e
    RequestHeader set X-Shib-displayName %{displayName}e
    RequestHeader set X-Shib-eduPersonPrincipalName %{eduPersonPrincipalName}e
    RequestHeader set X-Shib-Identity-Provider %{Shib-Identity-Provider}e
</VirtualHost>
```

### 4. Configure Nginx

Edit Nginx config:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.usc.edu;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        shib_request /shibauthorizer;
        shib_request_set $shib_session $upstream_http_shib_session_id;
        shib_request_set $shib_uid $upstream_http_shib_uid;
        shib_request_set $shib_mail $upstream_http_shib_mail;
        shib_request_set $shib_givenname $upstream_http_shib_givenname;
        shib_request_set $shib_sn $upstream_http_shib_sn;
        shib_request_set $shib_displayname $upstream_http_shib_displayname;
        shib_request_set $shib_eppn $upstream_http_shib_edupersonprincipalname;
        shib_request_set $shib_idp $upstream_http_shib_identity_provider;
        
        proxy_pass http://localhost:8000;
        proxy_set_header X-Shib-Session-ID $shib_session;
        proxy_set_header X-Shib-uid $shib_uid;
        proxy_set_header X-Shib-mail $shib_mail;
        proxy_set_header X-Shib-givenName $shib_givenname;
        proxy_set_header X-Shib-sn $shib_sn;
        proxy_set_header X-Shib-displayName $shib_displayname;
        proxy_set_header X-Shib-eduPersonPrincipalName $shib_eppn;
        proxy_set_header X-Shib-Identity-Provider $shib_idp;
    }
    
    location = /shibauthorizer {
        internal;
        proxy_pass http://localhost:8000;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
    }
}
```

## Registration with USC

### Required Steps

1. **Register Service with USC Directory Steering Committee**
   - Submit request at: http://www.usc.edu/gds/
   - Provide:
     - Service URL
     - Entity ID
     - Required attributes (uid, mail, givenName, sn, displayName)
     - Contact information

2. **Get Metadata**
   - USC will provide IdP metadata
   - Add to Shibboleth SP configuration

3. **Test with USC Test IdP**
   - Use test environment first
   - Verify attribute release
   - Test authentication flow

4. **Move to Production**
   - Update to production IdP
   - Final testing
   - Go live

## Application Configuration

### Environment Variables

Add to `.env`:

```bash
# USC Shibboleth Authentication
AUTH_ENABLED=true
AUTH_REQUIRED=true
USC_IDP_ENTITY_ID=https://idp.usc.edu/idp/shibboleth
SHIBBOLETH_SESSION_TIMEOUT_HOURS=8
```

### Development Mode

For local development without Shibboleth SP:

```bash
# Disable auth requirement
AUTH_ENABLED=false
AUTH_REQUIRED=false
```

Or set mock headers for testing:

```bash
# Mock Shibboleth headers (development only)
export uid=testuser
export mail=testuser@usc.edu
export givenName=Test
export sn=User
export displayName="Test User"
export Shib-Session-ID=test-session-123
```

## Protected Routes

### Require Authentication

```python
from internal.auth.shibboleth import require_auth

@app.get("/api/protected")
async def protected_endpoint(user = Depends(require_auth)):
    return {"message": f"Hello {user['display_name']}"}
```

### Optional Authentication

```python
from internal.auth.shibboleth import get_current_user

@app.get("/api/public")
async def public_endpoint(user = Depends(get_current_user)):
    if user:
        return {"message": f"Hello {user['display_name']}"}
    return {"message": "Hello guest"}
```

## Frontend Integration

The frontend automatically:
- Checks auth status on load
- Displays user name when authenticated
- Shows login link when not authenticated
- Shows logout link when authenticated

## Testing

### Test Authentication

1. Access application URL
2. Should redirect to USC login
3. Login with USC NetID
4. Redirected back to application
5. Should see your name in header

### Test Logout

1. Click "Logout" link
2. Should redirect to Shibboleth logout
3. Then redirect back to application
4. Should show "Not logged in"

## Troubleshooting

### Not Redirecting to Login

- Check Shibboleth SP is running: `systemctl status shibd`
- Check Apache/Nginx config has Shibboleth enabled
- Verify `shibboleth2.xml` configuration

### Headers Not Reaching Backend

- Check proxy configuration passes headers
- Verify header names match (X-Shib-*)
- Check FastAPI middleware is reading headers

### Authentication Not Working

- Verify USC IdP metadata is correct
- Check entity ID matches registration
- Review Shibboleth logs: `/var/log/shibboleth/`

## Security Considerations

1. **HTTPS Required**: Shibboleth requires SSL/TLS
2. **Session Timeout**: Configured to 8 hours (configurable)
3. **Attribute Release**: Only request necessary attributes
4. **Logging**: Log authentication events for security
5. **Error Handling**: Don't expose sensitive info in errors

## References

- [USC Shibboleth SP Installation](https://shibboleth.usc.edu/docs/sp/install/)
- [USC Global Directory Service](http://www.usc.edu/gds/)
- [Shibboleth Documentation](https://shibboleth.net/)

