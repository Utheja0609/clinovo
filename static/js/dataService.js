/**
 * DataService - A modular, production-ready HTTP client wrapper built around the Fetch API.
 * Supports JSON payloads, FormData (file uploads & standard forms), query params, and auth tokens.
 */
class DataService {
  /**
   * @param {Object} config - Service configuration options.
   * @param {string} [config.baseUrl=''] - The root URL for API requests.
   * @param {Object} [config.headers] - Default headers to send with requests.
   * @param {Function} [config.getAuthToken] - Optional async/sync function returning a Bearer token.
   */
  constructor(config = {}) {
    this.baseUrl = config.baseUrl || '';
    this.defaultHeaders = config.headers || {
      'Accept': 'application/json',
    };
    this.getAuthToken = config.getAuthToken || null;
  }

  /**
   * Internal helper to assemble headers, dynamic auth tokens, and manage Content-Type.
   */
  async _getHeaders(customHeaders = {}, isFormData = false) {
    const headers = { ...this.defaultHeaders, ...customHeaders };

    // Automatically set Content-Type to JSON if sending raw objects and not FormData
    if (!isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    // Do NOT manually set Content-Type for FormData; browser must set boundary automatically
    if (isFormData) {
      delete headers['Content-Type'];
    }

    // Inject dynamic Authorization header if token handler exists
    if (this.getAuthToken) {
      const token = await this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Helper to format query parameters onto an endpoint path.
   */
  _buildQueryString(params = {}) {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(val => searchParams.append(key, val));
        } else {
          searchParams.append(key, value);
        }
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : '';
  }

  /**
   * Core request executor with robust response handling and error formatting.
   */
  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const isFormData = options.body instanceof FormData;
    const headers = await this._getHeaders(options.headers, isFormData);

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      // Handle HTTP status errors (outside 200-299 range)
      if (!response.ok) {
        let errorData;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          errorData = await response.json();
        } else {
          const text = await response.text();
          errorData = { message: text || response.statusText || 'An error occurred' };
        }

        const error = new Error(errorData.message || `HTTP Error ${response.status}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      // Return null for 204 No Content
      if (response.status === 204) {
        return null;
      }

      // Auto-parse based on response content type
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      console.error(`[DataService Error] ${options.method || 'GET'} ${endpoint}:`, error.message);
      throw error;
    }
  }

  // ==========================================
  // Public CRUD & Form Methods
  // ==========================================

  /**
   * HTTP GET Request
   * @param {string} endpoint - API path (e.g., '/api/users')
   * @param {Object} [params] - URL query parameters
   * @param {Object} [options] - Additional fetch options
   */
  async get(endpoint, params = {}, options = {}) {
    const query = this._buildQueryString(params);
    return this._request(`${endpoint}${query}`, {
      method: 'GET',
      ...options,
    });
  }

  /**
   * HTTP POST Request (JSON or FormData)
   * @param {string} endpoint
   * @param {Object|FormData} data - Payload body
   * @param {Object} [options]
   */
  async post(endpoint, data = {}, options = {}) {
    const body = data instanceof FormData ? data : JSON.stringify(data);
    return this._request(endpoint, {
      method: 'POST',
      body,
      ...options,
    });
  }

  /**
   * HTTP PUT Request
   * @param {string} endpoint
   * @param {Object|FormData} data
   * @param {Object} [options]
   */
  async put(endpoint, data = {}, options = {}) {
    const body = data instanceof FormData ? data : JSON.stringify(data);
    return this._request(endpoint, {
      method: 'PUT',
      body,
      ...options,
    });
  }

  /**
   * HTTP PATCH Request
   * @param {string} endpoint
   * @param {Object|FormData} data
   * @param {Object} [options]
   */
  async patch(endpoint, data = {}, options = {}) {
    const body = data instanceof FormData ? data : JSON.stringify(data);
    return this._request(endpoint, {
      method: 'PATCH',
      body,
      ...options,
    });
  }

  /**
   * HTTP DELETE Request
   * @param {string} endpoint
   * @param {Object} [options]
   */
  async delete(endpoint, options = {}) {
    return this._request(endpoint, {
      method: 'DELETE',
      ...options,
    });
  }

  /**
   * Directly submits a HTML Form Element via AJAX
   * @param {string} endpoint 
   * @param {HTMLFormElement} formElement 
   * @param {Object} [options] 
   */
  async submitForm(endpoint, formElement, options = {}) {
    const formData = new FormData(formElement);
    return this.post(endpoint, formData, options);
  }
}

export default DataService;