import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  getUserData: () => ipcRenderer.invoke('get-user-data'),
  saveUserData: (data: any) => ipcRenderer.invoke('save-user-data', data),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getStoragePath: () => ipcRenderer.invoke('get-storage-path'),
  
  windowMinimize: () => ipcRenderer.invoke('window-minimize'),
  windowMaximize: () => ipcRenderer.invoke('window-maximize'),
  windowClose: () => ipcRenderer.invoke('window-close'),
  windowIsMaximized: () => ipcRenderer.invoke('window-is-maximized')
});
