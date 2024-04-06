import os
from pypylon import pylon


class UsbCam():
    type = ''
    serial_number = '22740654'
    camera = None
    image = None


    def initialize(self):
        tl_factory = pylon.TlFactory.GetInstance()
        self.camera = pylon.InstantCamera()
        self.camera.Attach(tl_factory.CreateFirstDevice())
    


    def show_devices(self):
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()
        for device in devices:
            print(device.GetFriendlyName())
        
        return devices
    

    
    def connect(self, serial):
        info = None
        for i in pylon.TlFactory.GetInstance().EnumerateDevices():
            if i.GetSerialNumber() == serial:
                info = i
                
                break
            else:
                print('Camera with {} serial number not found'.format(serial))

        if info is not None:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(info))
            self.camera.Open()
            return True
        else:
            return False
        
    
        


    def acquire_image(self):
        try:
        
            self.image = self.ForegroundAcquisition()   
            return self.image
        except:
            return None
    
        return None


    def ForegroundAcquisition(self):
        img = None
        if not self.camera.IsGrabbing():
            self.camera.StartGrabbingMax(3)
        
        while self.camera.IsGrabbing():
         
            img = self.camera.RetrieveResult(200)
            if img.GrabSucceeded():
                self.camera.StopGrabbing()
                
                return img.Array       
            else:
                raise RuntimeError("Grab failed")
    
        
        
        
    def camera_close(self):
        self.camera.Close()