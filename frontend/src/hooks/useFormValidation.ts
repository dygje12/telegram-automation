import { useState, useCallback, useMemo } from 'react';
import { z } from 'zod';

// Common validation schemas
export const validationSchemas = {
  phoneNumber: z.string()
    .min(10, 'Phone number must be at least 10 digits')
    .max(15, 'Phone number must not exceed 15 digits')
    .regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format'),

  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/\d/, 'Password must contain at least one number')
    .regex(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, 'Password must contain at least one special character'),

  email: z.string()
    .email('Invalid email format')
    .max(254, 'Email must not exceed 254 characters'),

  name: z.string()
    .min(1, 'Name is required')
    .max(50, 'Name must not exceed 50 characters')
    .regex(/^[a-zA-Z\s]+$/, 'Name can only contain letters and spaces'),

  message: z.string()
    .min(1, 'Message is required')
    .max(4096, 'Message must not exceed 4096 characters'),

  groupId: z.number()
    .int('Group ID must be an integer')
    .negative('Group ID must be negative for supergroups'),

  scheduleName: z.string()
    .min(1, 'Schedule name is required')
    .max(100, 'Schedule name must not exceed 100 characters'),

  url: z.string()
    .url('Invalid URL format')
    .max(2048, 'URL must not exceed 2048 characters'),
};

// Custom hook for form validation
export const useFormValidation = (schema, initialValues = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validate a single field
  const validateField = useCallback((name, value) => {
    try {
      if (schema.shape && schema.shape[name]) {
        schema.shape[name].parse(value);
        return null;
      }
      return null;
    } catch (error) {
      if (error instanceof z.ZodError) {
        return error.errors[0]?.message || 'Invalid value';
      }
      return 'Validation error';
    }
  }, [schema]);

  // Validate all fields
  const validateAll = useCallback(() => {
    try {
      schema.parse(values);
      setErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors = {};
        error.errors.forEach((err) => {
          const path = err.path.join('.');
          newErrors[path] = err.message;
        });
        setErrors(newErrors);
        return false;
      }
      return false;
    }
  }, [schema, values]);

  // Handle field change
  const handleChange = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  }, [errors]);

  // Handle field blur
  const handleBlur = useCallback((name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    
    const error = validateField(name, values[name]);
    if (error) {
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  }, [validateField, values]);

  // Handle form submission
  const handleSubmit = useCallback(async (onSubmit) => {
    setIsSubmitting(true);
    
    // Mark all fields as touched
    const allTouched = Object.keys(values).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);

    // Validate all fields
    const isValid = validateAll();
    
    if (isValid) {
      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
        throw error;
      }
    }
    
    setIsSubmitting(false);
    return isValid;
  }, [values, validateAll]);

  // Reset form
  const reset = useCallback((newValues = initialValues) => {
    setValues(newValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  // Set field error manually
  const setFieldError = useCallback((name, error) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  // Set multiple field errors
  const setFieldErrors = useCallback((newErrors) => {
    setErrors(prev => ({ ...prev, ...newErrors }));
  }, []);

  // Get field props for easy integration with form inputs
  const getFieldProps = useCallback((name) => ({
    value: values[name] || '',
    onChange: (e) => {
      const value = e.target ? e.target.value : e;
      handleChange(name, value);
    },
    onBlur: () => handleBlur(name),
    error: touched[name] && errors[name],
    name,
  }), [values, handleChange, handleBlur, touched, errors]);

  // Check if form is valid
  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0 && Object.keys(touched).length > 0;
  }, [errors, touched]);

  // Check if form has been modified
  const isDirty = useMemo(() => {
    return JSON.stringify(values) !== JSON.stringify(initialValues);
  }, [values, initialValues]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    isDirty,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    setFieldError,
    setFieldErrors,
    getFieldProps,
    validateField,
    validateAll,
  };
};

// Hook for async validation (e.g., checking if username exists)
export const useAsyncValidation = (asyncValidator, delay = 500) => {
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState(null);

  const validate = useCallback(
    debounce(async (value) => {
      if (!value) {
        setValidationError(null);
        return;
      }

      setIsValidating(true);
      try {
        const result = await asyncValidator(value);
        setValidationError(result.error || null);
      } catch (error) {
        setValidationError('Validation failed');
      } finally {
        setIsValidating(false);
      }
    }, delay),
    [asyncValidator, delay]
  );

  return {
    validate,
    isValidating,
    validationError,
  };
};

// Debounce utility
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Pre-built validation schemas for common forms
export const formSchemas = {
  login: z.object({
    phone_number: validationSchemas.phoneNumber,
    password: z.string().min(1, 'Password is required'),
  }),

  register: z.object({
    phone_number: validationSchemas.phoneNumber,
    password: validationSchemas.password,
    confirmPassword: z.string(),
    first_name: validationSchemas.name,
    last_name: validationSchemas.name,
  }).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  }),

  message: z.object({
    content: validationSchemas.message,
    template_name: z.string().min(1, 'Template name is required').max(100),
  }),

  group: z.object({
    group_id: validationSchemas.groupId,
    title: z.string().min(1, 'Group title is required').max(200),
    username: z.string().optional(),
  }),

  schedule: z.object({
    name: validationSchemas.scheduleName,
    message_template: validationSchemas.message,
    target_groups: z.array(z.number()).min(1, 'At least one group is required'),
    schedule_type: z.enum(['once', 'recurring']),
    scheduled_time: z.string().min(1, 'Scheduled time is required'),
    interval_minutes: z.number().min(1).optional(),
  }),

  settings: z.object({
    default_delay_min: z.number().min(1, 'Minimum delay must be at least 1 second'),
    default_delay_max: z.number().min(1, 'Maximum delay must be at least 1 second'),
    max_retries: z.number().min(0).max(10, 'Max retries cannot exceed 10'),
    enable_notifications: z.boolean(),
  }).refine((data) => data.default_delay_max >= data.default_delay_min, {
    message: "Maximum delay must be greater than or equal to minimum delay",
    path: ["default_delay_max"],
  }),
};

