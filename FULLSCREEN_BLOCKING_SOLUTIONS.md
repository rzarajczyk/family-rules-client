# macOS Fullscreen App Blocking Solutions

## Problem
The BlockWindow on macOS was not visible when fullscreen applications were running, making parental control ineffective in those scenarios.

## Root Causes
1. **Insufficient window level**: Using `kCGMaximumWindowLevel` doesn't work reliably with fullscreen apps
2. **Missing fullscreen auxiliary behavior**: Window didn't have proper collection behavior to appear in fullscreen spaces
3. **No shielding window level**: Not using the proper shielding window level designed for parental control applications
4. **Lack of accessibility permissions**: Some advanced window control features require accessibility permissions

## Implemented Solutions

### 1. Enhanced Window Level Management
- **CGShieldingWindowLevel**: Primary approach using the window level designed for parental controls
- **Fallback to kCGScreenSaverWindowLevel**: Secondary approach using screen saver level (1000)
- **Dynamic level reapplication**: Continuously reapply window level to ensure it stays above fullscreen apps

### 2. Fullscreen Auxiliary Collection Behavior
- **NSWindowCollectionBehaviorFullScreenAuxiliary**: Allows window to appear in fullscreen spaces
- **NSWindowCollectionBehaviorCanJoinAllSpaces**: Ensures window appears on all desktop spaces
- **NSWindowCollectionBehaviorStationary**: Prevents window from being moved
- **NSWindowCollectionBehaviorIgnoresCycle**: Prevents window from being cycled through

### 3. Accessibility Permissions
- **Permission checking**: Automatically check for accessibility permissions
- **Permission requesting**: Request permissions when needed
- **Graceful degradation**: Continue with reduced functionality if permissions aren't granted

### 4. Fullscreen App Detection and Fallback
- **AppleScript detection**: Use AppleScript to detect running fullscreen applications
- **Escape key injection**: Automatically send Escape key to exit fullscreen mode
- **Enhanced monitoring**: More frequent checks (50ms) when fullscreen apps are detected

### 5. Enhanced Window Management
- **Multiple ordering strategies**: Use both `orderFront:` and `makeKeyAndOrderFront:`
- **Mouse event handling**: Properly configure mouse event handling
- **Deactivation prevention**: Prevent window from hiding when deactivated

## Technical Implementation Details

### Window Level Strategy
```python
# Primary: CGShieldingWindowLevel + 1
shielding_level = core_graphics.CGShieldingWindowLevel()
window_level = c_int(shielding_level + 1)

# Fallback: kCGScreenSaverWindowLevel
kCGScreenSaverWindowLevel = 1000
```

### Collection Behavior
```python
behavior = (NSWindowCollectionBehaviorCanJoinAllSpaces | 
           NSWindowCollectionBehaviorStationary | 
           NSWindowCollectionBehaviorFullScreenAuxiliary |
           NSWindowCollectionBehaviorIgnoresCycle)
```

### Fullscreen Detection
```applescript
tell application "System Events"
    set fullscreenApps to {}
    repeat with proc in (every application process)
        try
            if (count of windows of proc) > 0 then
                set fullscreen to value of attribute "AXFullScreen" of window 1 of proc
                if fullscreen is true then
                    set end of fullscreenApps to name of proc
                end if
            end if
        end try
    end repeat
    return fullscreenApps
end tell
```

## Testing


### Test Procedure
1. Start a fullscreen application (YouTube, game, etc.)
2. Run the test script
3. Verify the blocking window appears over the fullscreen app
4. Test with different types of fullscreen applications

## Permissions Required

### Accessibility Permissions
The application may request accessibility permissions to:
- Detect fullscreen applications
- Send keyboard events (Escape key)
- Control window ordering

To grant permissions:
1. Go to System Preferences > Security & Privacy > Privacy
2. Select "Accessibility" from the left sidebar
3. Add the Family Rules application
4. Ensure it's checked/enabled

## Limitations and Considerations

### macOS Security
- Some fullscreen applications may still be able to override the blocking window
- System-level restrictions may prevent certain window level operations
- Accessibility permissions are required for full functionality

### Performance
- More frequent window level checks (50ms intervals) when fullscreen apps detected
- AppleScript execution for fullscreen detection adds some overhead
- Multiple window ordering operations may impact performance

### Compatibility
- Solutions are specifically designed for macOS
- May not work with all types of fullscreen applications
- Some applications may have their own window management that conflicts

## Future Enhancements

### Potential Improvements
1. **System-level hooks**: Implement lower-level system hooks for more reliable blocking
2. **Process monitoring**: Monitor specific applications and force them out of fullscreen
3. **User notifications**: Notify users when fullscreen apps are detected and blocked
4. **Configuration options**: Allow users to configure blocking behavior per application

### Alternative Approaches
1. **Screen Time integration**: Leverage macOS built-in Screen Time features
2. **Kernel extensions**: Use kernel extensions for system-level control (requires code signing)
3. **System preferences**: Integrate with macOS parental control settings

## Troubleshooting

### Common Issues
1. **Window not appearing**: Check accessibility permissions
2. **Still visible behind fullscreen**: Try the test script to verify functionality
3. **Performance issues**: Monitor system resources during blocking

### Debug Information
Enable debug logging to see detailed information about window level operations and fullscreen detection:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The enhanced blocking implementation provides multiple layers of protection against fullscreen applications:

1. **Primary**: CGShieldingWindowLevel with fullscreen auxiliary behavior
2. **Secondary**: Screen saver window level fallback
3. **Tertiary**: Fullscreen app detection and forced exit
4. **Quaternary**: Enhanced window ordering and accessibility controls

This multi-layered approach significantly improves the effectiveness of parental control blocking on macOS, even when fullscreen applications are running.

