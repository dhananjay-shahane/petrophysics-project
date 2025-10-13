# How to Upload LAS Files

## Quick Guide

### Using the Python Logs Panel (Recommended)

The Python Logs panel at the bottom of the screen now has built-in LAS file upload functionality!

**Steps:**

1. **Open a Project**
   - Go to Project → New or Project → Open
   - Select or create your project

2. **Upload LAS File**
   - Look at the Python Logs panel at the bottom
   - Click "Choose LAS File" button
   - Select your .las file from your computer
   - Click "Upload" button

3. **Watch the Logs**
   - The panel will show real-time progress logs:
     ```
     Starting LAS file upload...
     File selected: your-well.las
     Saving file as: your-well.las
     Parsing LAS file...
     LAS file parsed successfully
     Well Name: WELL-001
     Well Type: Dev
     Found 25 log curves
     Saving well to project...
     SUCCESS: Well saved to: /path/to/well.ptrc
     SUCCESS: LAS file copied to: /path/to/las-file.las
     Well "WELL-001" created successfully!
     ```

4. **Auto-Scroll**
   - Logs automatically scroll to show the latest messages
   - Scroll up to view previous logs
   - Click "Clear" to remove old logs

## Log Colors

- **Blue** - Information messages
- **Green** - Success messages  
- **Red** - Error messages
- **Yellow** - Warning messages

## Features

✅ **Direct Upload** - No need to open separate dialogs
✅ **Real-time Feedback** - See exactly what's happening
✅ **Auto-scroll** - Latest logs always visible
✅ **Error Details** - Clear error messages if something fails
✅ **Progress Tracking** - Know the upload status at every step

## Troubleshooting

**"No project is currently open"**
- Make sure you've opened or created a project first
- Check that Project Path shows a valid path (not "No path selected")

**Upload fails**
- Check the error message in red in the logs
- Verify the LAS file is valid
- Ensure the project folder exists and is accessible

**Logs not showing**
- The Python Logs panel auto-scrolls to bottom
- Scroll down manually if needed
- Click "Clear" and try uploading again
