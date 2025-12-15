# Vercel Deployment Troubleshooting

## Configuration Conflicts

✅ **No conflicts found:**
- No `now.json` file (only `vercel.json` exists)
- No `.nowignore` file (only `.vercelignore` exists)
- No `.now` directory

## Current Configuration

### Files
- `vercel.json` - Main Vercel configuration
- `api/index.py` - Serverless function entry point
- `requirements.txt` - Python dependencies (root level)
- `.vercelignore` - Files to ignore during deployment

### Function Settings
- **Memory**: 1024 MB
- **Max Duration**: 30 seconds
- **Python Version**: 3.11

## Common Issues

### 1. Function Crashes
**Symptoms**: 500 error, FUNCTION_INVOCATION_FAILED

**Possible Causes**:
- Import path issues
- Missing dependencies
- File system permissions

**Solution**: Check Vercel logs for detailed error messages

### 2. Import Errors
**Symptoms**: ImportError in logs

**Solution**: 
- Ensure `requirements.txt` is at project root
- Check that all Python paths are correctly set in `api/index.py`
- Verify backend files are included in deployment

### 3. File System Issues
**Symptoms**: Permission errors when creating directories

**Solution**:
- Use `/tmp` for writable data (already configured)
- Templates/static files must exist in repo (read-only on Vercel)

## Debugging

1. **Check Logs**: Vercel Dashboard → Functions → Logs
2. **Test Endpoint**: Visit URL to see error JSON response
3. **Verify Files**: Ensure all files are committed to GitHub

## Next Steps

If deployment still fails:
1. Check Vercel build logs
2. Review error JSON response from endpoint
3. Verify all dependencies in `requirements.txt`
4. Consider alternative platform (Railway/Render) for better Python support

