# Progress Storage

## How Progress Works

Your Junimo app now stores progress **locally in your browser** using localStorage. This means:

### ✅ **Benefits:**
- **Private Progress**: Your progress is personal to you and your browser
- **No Account Required**: No need to sign up or log in
- **Offline Storage**: Progress is saved even when offline
- **Fast Performance**: No server requests needed for progress updates

### 📱 **Per-Browser Storage:**
- Progress is stored separately in each browser/device
- Chrome progress ≠ Safari progress ≠ Mobile browser progress
- Each user gets their own independent progress tracking

### 🔄 **Managing Progress:**
- **Automatic Save**: Progress is automatically saved when you check/uncheck items
- **Clear Progress**: Use the "Clear All Progress" button in the Progress tab
- **Persistent**: Progress survives browser restarts and page refreshes

### 🔧 **Technical Details:**
- Uses browser's `localStorage` API
- Data format: JSON array of completed bundle items
- Storage key: `junimo-progress`
- No server-side storage or database writes for progress

### 🚨 **Important Notes:**
- **Browser-Specific**: Progress doesn't sync between different browsers
- **Local Only**: Clearing browser data will remove progress
- **No Backup**: Progress is not backed up to any server
- **Privacy**: Your progress never leaves your device

This design ensures that each player has their own private progress tracking without needing accounts or server-side user management.