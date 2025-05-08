from algopy import ARC4Contract, arc4, Bytes, UInt64

class Record(ARC4Contract):
    # Define structs as classes
    class Patient:
        def __init__(self):
            self.ic: arc4.String = arc4.String("")
            self.name: arc4.String = arc4.String("")
            self.phone: arc4.String = arc4.String("")
            self.gender: arc4.String = arc4.String("")
            self.dob: arc4.String = arc4.String("")
            self.height: arc4.String = arc4.String("")
            self.weight: arc4.String = arc4.String("")
            self.houseaddr: arc4.String = arc4.String("")
            self.bloodgroup: arc4.String = arc4.String("")
            self.allergies: arc4.String = arc4.String("")
            self.medication: arc4.String = arc4.String("")
            self.emergencyName: arc4.String = arc4.String("")
            self.emergencyContact: arc4.String = arc4.String("")
            self.addr: Bytes = Bytes("")
            self.date: UInt64 = UInt64(0)

    class Doctor:
        def __init__(self):
            self.ic: arc4.String = arc4.String("")
            self.name: arc4.String = arc4.String("")
            self.phone: arc4.String = arc4.String("")
            self.gender: arc4.String = arc4.String("")
            self.dob: arc4.String = arc4.String("")
            self.qualification: arc4.String = arc4.String("")
            self.major: arc4.String = arc4.String("")
            self.addr: Bytes = Bytes("")
            self.date: UInt64 = UInt64(0)

    class Appointment:
        def __init__(self):
            self.doctoraddr: Bytes = Bytes("")
            self.patientaddr: Bytes = Bytes("")
            self.date: arc4.String = arc4.String("")
            self.time: arc4.String = arc4.String("")
            self.prescription: arc4.String = arc4.String("")
            self.description: arc4.String = arc4.String("")
            self.diagnosis: arc4.String = arc4.String("")
            self.status: arc4.String = arc4.String("")
            self.creationDate: UInt64 = UInt64(0)

    def __init__(self):
        # Initialize state variables
        self.owner = arc4.Address()
        self.patientList = arc4.DynamicArray[arc4.Address]()
        self.doctorList = arc4.DynamicArray[arc4.Address]()
        self.appointmentList = arc4.DynamicArray[arc4.Address]()
        
        # Mappings
        self.patients = arc4.Mapping[arc4.Address, Record.Patient]()
        self.doctors = arc4.Mapping[arc4.Address, Record.Doctor]()
        self.appointments = arc4.Mapping[arc4.Address, Record.Appointment]()
        
        self.isApproved = arc4.Mapping[arc4.Address, arc4.Mapping[arc4.Address, arc4.Bool]]()
        self.isPatient = arc4.Mapping[arc4.Address, arc4.Bool]()
        self.isDoctor = arc4.Mapping[arc4.Address, arc4.Bool]()
        self.AppointmentPerPatient = arc4.Mapping[arc4.Address, UInt64]()
        
        # Counters
        self.patientCount = UInt64(0)
        self.doctorCount = UInt64(0)
        self.appointmentCount = UInt64(0)
        self.permissionGrantedCount = UInt64(0)
        
        # Set owner to transaction sender
        self.owner = arc4.Address(arc4.txn.sender())

    @arc4.abimethod
    def setDetails(self, _ic: arc4.String, _name: arc4.String, _phone: arc4.String, 
                  _gender: arc4.String, _dob: arc4.String, _height: arc4.String, 
                  _weight: arc4.String, _houseaddr: arc4.String, _bloodgroup: arc4.String, 
                  _allergies: arc4.String, _medication: arc4.String, 
                  _emergencyName: arc4.String, _emergencyContact: arc4.String) -> None:
        sender = arc4.Address(arc4.txn.sender())
        assert not self.isPatient[sender], "Already registered as patient"
        
        p = Record.Patient()
        p.ic = _ic
        p.name = _name
        p.phone = _phone
        p.gender = _gender
        p.dob = _dob
        p.height = _height
        p.weight = _weight
        p.houseaddr = _houseaddr
        p.bloodgroup = _bloodgroup
        p.allergies = _allergies
        p.medication = _medication
        p.emergencyName = _emergencyName
        p.emergencyContact = _emergencyContact
        p.addr = sender
        p.date = arc4.txn.first_valid()
        
        self.patients[sender] = p
        self.patientList.append(sender)
        self.isPatient[sender] = arc4.Bool(True)
        self.isApproved[sender][sender] = arc4.Bool(True)
        self.patientCount += UInt64(1)

    @arc4.abimethod
    def editDetails(self, _ic: arc4.String, _name: arc4.String, _phone: arc4.String, 
                   _gender: arc4.String, _dob: arc4.String, _height: arc4.String, 
                   _weight: arc4.String, _houseaddr: arc4.String, _bloodgroup: arc4.String, 
                   _allergies: arc4.String, _medication: arc4.String, 
                   _emergencyName: arc4.String, _emergencyContact: arc4.String) -> None:
        sender = arc4.Address(arc4.txn.sender())
        assert self.isPatient[sender], "Not registered as patient"
        
        p = self.patients[sender]
        p.ic = _ic
        p.name = _name
        p.phone = _phone
        p.gender = _gender
        p.dob = _dob
        p.height = _height
        p.weight = _weight
        p.houseaddr = _houseaddr
        p.bloodgroup = _bloodgroup
        p.allergies = _allergies
        p.medication = _medication
        p.emergencyName = _emergencyName
        p.emergencyContact = _emergencyContact
        p.addr = sender
        
        self.patients[sender] = p

    @arc4.abimethod
    def setDoctor(self, _ic: arc4.String, _name: arc4.String, _phone: arc4.String, 
                 _gender: arc4.String, _dob: arc4.String, _qualification: arc4.String, 
                 _major: arc4.String) -> None:
        sender = arc4.Address(arc4.txn.sender())
        assert not self.isDoctor[sender], "Already registered as doctor"
        
        d = Record.Doctor()
        d.ic = _ic
        d.name = _name
        d.phone = _phone
        d.gender = _gender
        d.dob = _dob
        d.qualification = _qualification
        d.major = _major
        d.addr = sender
        d.date = arc4.txn.first_valid()
        
        self.doctors[sender] = d
        self.doctorList.append(sender)
        self.isDoctor[sender] = arc4.Bool(True)
        self.doctorCount += UInt64(1)

    @arc4.abimethod
    def editDoctor(self, _ic: arc4.String, _name: arc4.String, _phone: arc4.String, 
                  _gender: arc4.String, _dob: arc4.String, _qualification: arc4.String, 
                  _major: arc4.String) -> None:
        sender = arc4.Address(arc4.txn.sender())
        assert self.isDoctor[sender], "Not registered as doctor"
        
        d = self.doctors[sender]
        d.ic = _ic
        d.name = _name
        d.phone = _phone
        d.gender = _gender
        d.dob = _dob
        d.qualification = _qualification
        d.major = _major
        d.addr = sender
        
        self.doctors[sender] = d

    @arc4.abimethod
    def setAppointment(self, _addr: arc4.Address, _date: arc4.String, _time: arc4.String, 
                      _diagnosis: arc4.String, _prescription: arc4.String, 
                      _description: arc4.String, _status: arc4.String) -> None:
        sender = arc4.Address(arc4.txn.sender())
        assert self.isDoctor[sender], "Not registered as doctor"
        
        a = Record.Appointment()
        a.doctoraddr = sender
        a.patientaddr = _addr
        a.date = _date
        a.time = _time
        a.diagnosis = _diagnosis
        a.prescription = _prescription
        a.description = _description
        a.status = _status
        a.creationDate = arc4.txn.first_valid()
        
        self.appointments[_addr] = a
        self.appointmentList.append(_addr)
        self.appointmentCount += UInt64(1)
        self.AppointmentPerPatient[_addr] += UInt64(1)

    @arc4.abimethod
    def updateAppointment(self, _addr: arc4.Address, _date: arc4.String, _time: arc4.String, 
                         _diagnosis: arc4.String, _prescription: arc4.String, 
                         _description: arc4.String, _status: arc4.String) -> None:
        sender = arc4.Address(arc4.txn.sender())
        assert self.isDoctor[sender], "Not registered as doctor"
        
        a = self.appointments[_addr]
        a.doctoraddr = sender
        a.patientaddr = _addr
        a.date = _date
        a.time = _time
        a.diagnosis = _diagnosis
        a.prescription = _prescription
        a.description = _description
        a.status = _status
        
        self.appointments[_addr] = a

    @arc4.abimethod
    def givePermission(self, _address: arc4.Address) -> arc4.Bool:
        sender = arc4.Address(arc4.txn.sender())
        self.isApproved[sender][_address] = arc4.Bool(True)
        self.permissionGrantedCount += UInt64(1)
        return arc4.Bool(True)

    @arc4.abimethod
    def revokePermission(self, _address: arc4.Address) -> arc4.Bool:
        sender = arc4.Address(arc4.txn.sender())
        self.isApproved[sender][_address] = arc4.Bool(False)
        return arc4.Bool(True)

    @arc4.abimethod
    def getPatients(self) -> arc4.DynamicArray[arc4.Address]:
        return self.patientList

    @arc4.abimethod
    def getDoctors(self) -> arc4.DynamicArray[arc4.Address
