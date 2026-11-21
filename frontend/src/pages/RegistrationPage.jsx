import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  getClinics, 
  getDepartments, 
  getDoctors, 
  registerPatient 
} from '../services/api';
import { 
  UserPlus, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Building2, 
  Stethoscope, 
  Globe2, 
  Phone, 
  User, 
  Ticket, 
  Calendar, 
  Clock, 
  ArrowLeft,
  RefreshCw
} from 'lucide-react';

const RegistrationPage = () => {
  // Cascading Dropdown States
  const [clinics, setClinics] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);

  // Form Fields
  const [fullName, setFullName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [selectedClinicId, setSelectedClinicId] = useState('');
  const [selectedDepartmentId, setSelectedDepartmentId] = useState('');
  const [selectedDoctorId, setSelectedDoctorId] = useState('');

  // UI States
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadingDepartments, setLoadingDepartments] = useState(false);
  const [loadingDoctors, setLoadingDoctors] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [registrationResult, setRegistrationResult] = useState(null);

  // 1. Load Clinics on Initial Mount
  useEffect(() => {
    const fetchClinics = async () => {
      setLoadingInitial(true);
      setErrorMessage(null);
      try {
        const data = await getClinics();
        setClinics(data);
        if (data.length > 0) {
          setSelectedClinicId(data[0].id);
        }
      } catch (err) {
        setErrorMessage(
          err.response?.data?.detail || 
          'Failed to load clinics. Ensure the FastAPI backend is running.'
        );
      } finally {
        setLoadingInitial(false);
      }
    };
    fetchClinics();
  }, []);

  // 2. Load Departments when Clinic changes
  useEffect(() => {
    if (!selectedClinicId) {
      setDepartments([]);
      setSelectedDepartmentId('');
      return;
    }

    const fetchDepartments = async () => {
      setLoadingDepartments(true);
      try {
        const data = await getDepartments(selectedClinicId);
        setDepartments(data);
        if (data.length > 0) {
          setSelectedDepartmentId(data[0].id);
        } else {
          setSelectedDepartmentId('');
        }
      } catch (err) {
        setErrorMessage('Failed to load departments for the selected clinic.');
      } finally {
        setLoadingDepartments(false);
      }
    };
    fetchDepartments();
  }, [selectedClinicId]);

  // 3. Load Doctors when Department changes
  useEffect(() => {
    if (!selectedDepartmentId) {
      setDoctors([]);
      setSelectedDoctorId('');
      return;
    }

    const fetchDoctors = async () => {
      setLoadingDoctors(true);
      try {
        const data = await getDoctors(selectedDepartmentId);
        setDoctors(data);
        if (data.length > 0) {
          setSelectedDoctorId(data[0].id);
        } else {
          setSelectedDoctorId('');
        }
      } catch (err) {
        setErrorMessage('Failed to load doctors for the selected department.');
      } finally {
        setLoadingDoctors(false);
      }
    };
    fetchDoctors();
  }, [selectedDepartmentId]);

  // Handle Form Submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(null);

    // Basic Client-Side Validation
    if (!fullName.trim() || fullName.trim().length < 2) {
      setErrorMessage('Please provide the patient full name (at least 2 characters).');
      return;
    }

    const cleanPhone = phoneNumber.replace(/[\s\-\(\)]/g, '');
    if (!cleanPhone || cleanPhone.length < 10) {
      setErrorMessage('Please provide a valid 10-digit mobile number.');
      return;
    }

    if (!selectedClinicId || !selectedDepartmentId || !selectedDoctorId) {
      setErrorMessage('Please select a valid clinic, department, and doctor.');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        full_name: fullName.trim(),
        phone_number: cleanPhone,
        preferred_language: preferredLanguage,
        clinic_id: selectedClinicId,
        department_id: selectedDepartmentId,
        doctor_id: selectedDoctorId,
        registration_source: 'WEB',
      };

      const result = await registerPatient(payload);
      setRegistrationResult(result);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setErrorMessage(detail.map((d) => d.msg).join(', '));
      } else {
        setErrorMessage(detail || 'Registration failed. Please check backend connection.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Reset form to register another patient
  const handleRegisterAnother = () => {
    setRegistrationResult(null);
    setFullName('');
    setPhoneNumber('');
    setErrorMessage(null);
  };

  // --------------------------------------------------------------------------
  // SUCCESS CONFIRMATION VIEW
  // --------------------------------------------------------------------------
  if (registrationResult) {
    return (
      <div className="py-12 max-w-2xl mx-auto px-4 sm:px-6">
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden">
          {/* Header Banner */}
          <div className="bg-gradient-to-r from-teal-600 to-emerald-600 px-8 py-6 text-white text-center">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-white/20 backdrop-blur mb-3 shadow-inner">
              <CheckCircle2 className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-2xl font-black tracking-tight">Patient Registered Successfully!</h1>
            <p className="text-teal-100 text-sm mt-1">
              Your hospital queue token has been generated.
            </p>
          </div>

          <div className="p-8 space-y-6">
            {/* Primary Token Display Card */}
            <div className="text-center py-6 px-4 rounded-2xl bg-teal-50/80 border-2 border-dashed border-teal-300">
              <span className="text-xs uppercase tracking-widest font-bold text-teal-700 block">
                Queue Token Number
              </span>
              <div className="text-5xl sm:text-6xl font-black text-slate-900 tracking-tight my-2">
                {registrationResult.token_number}
              </div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Status: {registrationResult.status}</span>
              </div>
            </div>

            {/* Registration Details Breakdown */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium block">Patient Name</span>
                <span className="font-bold text-slate-900">{registrationResult.patient_name}</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium block">Mobile Number</span>
                <span className="font-bold text-slate-900 font-mono">
                  {registrationResult.patient_phone_masked}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium block">Clinic / Facility</span>
                <span className="font-bold text-slate-900">{registrationResult.clinic_name}</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium block">Department</span>
                <span className="font-bold text-slate-900">
                  {registrationResult.department_name} ({registrationResult.department_code})
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium block">Consulting Doctor</span>
                <span className="font-bold text-slate-900">{registrationResult.doctor_name}</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium block">Date & Registration Time</span>
                <span className="font-bold text-slate-900 text-xs">
                  {new Date(registrationResult.registration_time).toLocaleString()}
                </span>
              </div>
            </div>

            {registrationResult.duplicate_warning && (
              <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>
                  Notice: Patient already holds an active token for this department today. A new token was issued per walk-in request.
                </span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="pt-4 flex flex-col sm:flex-row items-center gap-3">
              <button
                onClick={handleRegisterAnother}
                className="w-full sm:w-1/2 py-3 px-4 rounded-xl text-sm font-semibold bg-teal-600 hover:bg-teal-700 text-white shadow-sm transition-colors flex items-center justify-center space-x-2"
              >
                <UserPlus className="h-4 w-4" />
                <span>Register Another Patient</span>
              </button>

              <Link
                to="/"
                className="w-full sm:w-1/2 py-3 px-4 rounded-xl text-sm font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors flex items-center justify-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Return to Overview</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // PATIENT REGISTRATION FORM VIEW
  // --------------------------------------------------------------------------
  return (
    <div className="py-10 max-w-3xl mx-auto px-4 sm:px-6">
      {/* Back button */}
      <div className="mb-6">
        <Link
          to="/"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-teal-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Project Home</span>
        </Link>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Form Header */}
        <div className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-2xl bg-teal-600 text-white flex items-center justify-center shadow-sm shadow-teal-500/20">
              <UserPlus className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900">Walk-in Patient Registration</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Generate an immediate daily queue token for hospital consultation (Checkpoint 2)
              </p>
            </div>
          </div>
        </div>

        {/* Error Alert Banner */}
        {errorMessage && (
          <div className="mx-8 mt-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="flex-grow">
              <p className="font-semibold">Registration Notice</p>
              <p className="text-xs text-rose-700 mt-0.5">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Initial Loading Skeleton */}
        {loadingInitial ? (
          <div className="p-12 text-center space-y-3">
            <Loader2 className="h-8 w-8 text-teal-600 animate-spin mx-auto" />
            <p className="text-sm text-slate-500 font-medium">Loading hospital clinics and departments...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-8 space-y-6">
            {/* Section 1: Patient Details */}
            <div className="space-y-4">
              <h2 className="text-xs uppercase tracking-wider font-bold text-teal-800 border-b border-slate-100 pb-2 flex items-center space-x-2">
                <User className="h-4 w-4" />
                <span>1. Patient Identification</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Full Name */}
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Patient Full Name <span className="text-rose-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      required
                      placeholder="e.g. Ramesh Kumar"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 text-sm text-slate-800"
                    />
                  </div>
                </div>

                {/* Mobile Number */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Mobile Number <span className="text-rose-500">*</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <Phone className="h-4 w-4" />
                    </div>
                    <input
                      type="tel"
                      required
                      placeholder="e.g. 9876543210"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 text-sm text-slate-800 font-mono"
                    />
                  </div>
                  <span className="text-[11px] text-slate-400 mt-1 block">
                    10-digit number or international (+91...) format
                  </span>
                </div>

                {/* Preferred Language */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Preferred Language <span className="text-rose-500">*</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <Globe2 className="h-4 w-4" />
                    </div>
                    <select
                      value={preferredLanguage}
                      onChange={(e) => setPreferredLanguage(e.target.value)}
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 text-sm text-slate-800 bg-white"
                    >
                      <option value="en">English</option>
                      <option value="hi">हिंदी (Hindi)</option>
                      <option value="mr">मराठी (Marathi)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Section 2: Clinical Facility & Consultation Routing */}
            <div className="space-y-4 pt-2">
              <h2 className="text-xs uppercase tracking-wider font-bold text-teal-800 border-b border-slate-100 pb-2 flex items-center space-x-2">
                <Building2 className="h-4 w-4" />
                <span>2. Clinic, Department & Doctor Selection</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Clinic Dropdown */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Clinic <span className="text-rose-500">*</span>
                  </label>
                  <select
                    value={selectedClinicId}
                    onChange={(e) => setSelectedClinicId(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 text-sm text-slate-800 bg-white"
                  >
                    {clinics.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Department Dropdown */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
                    <span>Department</span>
                    {loadingDepartments && <Loader2 className="h-3 w-3 animate-spin text-teal-600" />}
                  </label>
                  <select
                    value={selectedDepartmentId}
                    onChange={(e) => setSelectedDepartmentId(e.target.value)}
                    disabled={loadingDepartments || departments.length === 0}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 text-sm text-slate-800 bg-white disabled:bg-slate-100"
                  >
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name} ({d.code})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Doctor Dropdown */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
                    <span>Doctor</span>
                    {loadingDoctors && <Loader2 className="h-3 w-3 animate-spin text-teal-600" />}
                  </label>
                  <select
                    value={selectedDoctorId}
                    onChange={(e) => setSelectedDoctorId(e.target.value)}
                    disabled={loadingDoctors || doctors.length === 0}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 text-sm text-slate-800 bg-white disabled:bg-slate-100"
                  >
                    {doctors.map((doc) => (
                      <option key={doc.id} value={doc.id}>
                        {doc.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={submitting || !selectedDoctorId}
                className="w-full py-3.5 px-6 rounded-xl font-bold text-sm text-white bg-teal-600 hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-teal-600/20 transition-all flex items-center justify-center space-x-2"
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Processing Registration & Token...</span>
                  </>
                ) : (
                  <>
                    <Ticket className="h-4 w-4" />
                    <span>Issue Walk-in Queue Token</span>
                  </>
                )}
              </button>
              <p className="text-center text-xs text-slate-400 mt-2">
                Token sequences are atomic and safe under concurrent walk-in loads.
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default RegistrationPage;
