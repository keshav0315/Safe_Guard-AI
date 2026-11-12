/**
 * SafeGuard AI — Interactive Test Suite JavaScript Engine
 * Handles State, API Communication, Token Lifecycle, Live Inspector & UI Interactions
 */

(() => {
  'use strict';

  // ---------------------------------------------------------------------------
  // Global State
  // ---------------------------------------------------------------------------
  const state = {
    baseUrl: localStorage.getItem('sg_base_url') || 'http://127.0.0.1:8000',
    accessToken: localStorage.getItem('sg_access_token') || '',
    refreshToken: localStorage.getItem('sg_refresh_token') || '',
    currentUser: JSON.parse(localStorage.getItem('sg_current_user') || 'null'),
    theme: localStorage.getItem('sg_theme') || 'dark',
    history: JSON.parse(localStorage.getItem('sg_req_history') || '[]'),
    lastRegistered: JSON.parse(localStorage.getItem('sg_last_registered') || 'null'),
    tokenTimerInterval: null,
  };

  // ---------------------------------------------------------------------------
  // DOM Elements Cache
  // ---------------------------------------------------------------------------
  const dom = {
    baseUrlInput: document.getElementById('baseUrlInput'),
    pingBtn: document.getElementById('pingBtn'),
    backendStatusPill: document.getElementById('backendStatusPill'),
    backendStatusDot: document.getElementById('backendStatusDot'),
    backendStatusText: document.getElementById('backendStatusText'),
    authStatusUser: document.getElementById('authStatusUser'),
    quickLogoutBtn: document.getElementById('quickLogoutBtn'),
    swaggerLink: document.getElementById('swaggerLink'),
    openSwaggerBtn: document.getElementById('openSwaggerBtn'),
    openAdminBtn: document.getElementById('openAdminBtn'),
    themeToggleBtn: document.getElementById('themeToggleBtn'),
    themeIcon: document.getElementById('themeIcon'),
    toastContainer: document.getElementById('toastContainer'),

    // Tab buttons & panes
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),

    // Health cards
    healthCardStatus: document.getElementById('healthCardStatus'),
    healthCardLatency: document.getElementById('healthCardLatency'),
    healthCardVersion: document.getElementById('healthCardVersion'),
    runHealthCheckBtn: document.getElementById('runHealthCheckBtn'),

    // Registration form
    registerForm: document.getElementById('registerForm'),
    regEmail: document.getElementById('regEmail'),
    regDisplayName: document.getElementById('regDisplayName'),
    regPhone: document.getElementById('regPhone'),
    regLang: document.getElementById('regLang'),
    regPassword: document.getElementById('regPassword'),
    regPasswordConfirm: document.getElementById('regPasswordConfirm'),
    fillSampleRegisterBtn: document.getElementById('fillSampleRegisterBtn'),

    // Login form
    loginForm: document.getElementById('loginForm'),
    loginEmail: document.getElementById('loginEmail'),
    loginPassword: document.getElementById('loginPassword'),
    rememberMe: document.getElementById('rememberMe'),

    // Token displays & actions
    tokenExpiryBadge: document.getElementById('tokenExpiryBadge'),
    accessTokenDisplay: document.getElementById('accessTokenDisplay'),
    refreshTokenDisplay: document.getElementById('refreshTokenDisplay'),
    copyAccessTokenBtn: document.getElementById('copyAccessTokenBtn'),
    copyRefreshTokenBtn: document.getElementById('copyRefreshTokenBtn'),
    decodedTokenBox: document.getElementById('decodedTokenBox'),
    decodedPayloadContent: document.getElementById('decodedPayloadContent'),
    tokenTimerText: document.getElementById('tokenTimerText'),
    refreshTokenBtn: document.getElementById('refreshTokenBtn'),
    blacklistTokenBtn: document.getElementById('blacklistTokenBtn'),
    clearTokensBtn: document.getElementById('clearTokensBtn'),

    // Profile
    fetchProfileBtn: document.getElementById('fetchProfileBtn'),
    profileAuthIndicator: document.getElementById('profileAuthIndicator'),
    profileDetailsCard: document.getElementById('profileDetailsCard'),
    profileAvatar: document.getElementById('profileAvatar'),
    profileNameDisplay: document.getElementById('profileNameDisplay'),
    profileEmailDisplay: document.getElementById('profileEmailDisplay'),
    profileRoleBadge: document.getElementById('profileRoleBadge'),
    profilePhoneDisplay: document.getElementById('profilePhoneDisplay'),
    profileLangDisplay: document.getElementById('profileLangDisplay'),
    profileGuardianDisplay: document.getElementById('profileGuardianDisplay'),
    profileBioDisplay: document.getElementById('profileBioDisplay'),
    profileEmergencyMsgDisplay: document.getElementById('profileEmergencyMsgDisplay'),
    profileUpdateForm: document.getElementById('profileUpdateForm'),
    editDisplayName: document.getElementById('editDisplayName'),
    editPhone: document.getElementById('editPhone'),
    editLang: document.getElementById('editLang'),
    editBio: document.getElementById('editBio'),
    editEmergencyMessage: document.getElementById('editEmergencyMessage'),

    // SOS
    sosForm: document.getElementById('sosForm'),
    sosEventType: document.getElementById('sosEventType'),
    sosIdempotencyKey: document.getElementById('sosIdempotencyKey'),
    regenerateIdempotencyBtn: document.getElementById('regenerateIdempotencyBtn'),
    sosNotes: document.getElementById('sosNotes'),
    sosLatitude: document.getElementById('sosLatitude'),
    sosLongitude: document.getElementById('sosLongitude'),
    sosAccuracy: document.getElementById('sosAccuracy'),
    locPresetBtns: document.querySelectorAll('.loc-preset-btn'),
    getCurrentGeoBtn: document.getElementById('getCurrentGeoBtn'),
    fetchEmergencyHistoryBtn: document.getElementById('fetchEmergencyHistoryBtn'),

    // Custom
    customReqForm: document.getElementById('customReqForm'),
    customMethod: document.getElementById('customMethod'),
    customPath: document.getElementById('customPath'),
    customAttachToken: document.getElementById('customAttachToken'),
    customBody: document.getElementById('customBody'),
    prettifyJsonBtn: document.getElementById('prettifyJsonBtn'),
    customChips: document.querySelectorAll('.custom-chip'),

    // Live Inspector
    inspectMethodPill: document.getElementById('inspectMethodPill'),
    inspectStatusPill: document.getElementById('inspectStatusPill'),
    inspectLatencyPill: document.getElementById('inspectLatencyPill'),
    inspectUrlText: document.getElementById('inspectUrlText'),
    tabBtnBody: document.getElementById('tabBtnBody'),
    tabBtnReq: document.getElementById('tabBtnReq'),
    tabBtnHeaders: document.getElementById('tabBtnHeaders'),
    tabBtnHistory: document.getElementById('tabBtnHistory'),
    viewBody: document.getElementById('viewBody'),
    viewReq: document.getElementById('viewReq'),
    viewHeaders: document.getElementById('viewHeaders'),
    viewHistory: document.getElementById('viewHistory'),
    jsonViewer: document.getElementById('jsonViewer'),
    requestViewer: document.getElementById('requestViewer'),
    headersViewer: document.getElementById('headersViewer'),
    historyList: document.getElementById('historyList'),
    clearHistoryBtn: document.getElementById('clearHistoryBtn'),
    copyJsonBtn: document.getElementById('copyJsonBtn'),
  };

  // ---------------------------------------------------------------------------
  // Helper: UUID Generator (v4 compliant)
  // ---------------------------------------------------------------------------
  function generateUUID() {
    if (crypto && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  // ---------------------------------------------------------------------------
  // Helper: Toast Notifications
  // ---------------------------------------------------------------------------
  function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    const borderColors = {
      success: 'border-emerald-500 bg-emerald-950/90 text-emerald-200',
      error: 'border-rose-500 bg-rose-950/90 text-rose-200',
      warning: 'border-amber-500 bg-amber-950/90 text-amber-200',
      info: 'border-indigo-500 bg-slate-900/95 text-slate-200',
    };
    const iconNames = {
      success: 'check-circle-2',
      error: 'alert-triangle',
      warning: 'alert-circle',
      info: 'info',
    };

    toast.className = `pointer-events-auto p-3 rounded-xl border shadow-lg text-xs flex items-start space-x-2.5 backdrop-blur toast-enter ${borderColors[type] || borderColors.info}`;
    toast.innerHTML = `
      <i data-lucide="${iconNames[type] || 'info'}" class="w-4 h-4 mt-0.5 shrink-0"></i>
      <div class="flex-1 font-medium leading-relaxed">${escapeHtml(message)}</div>
      <button class="shrink-0 text-slate-400 hover:text-white p-0.5 ml-2" onclick="this.parentElement.remove()">
        <i data-lucide="x" class="w-3.5 h-3.5"></i>
      </button>
    `;

    dom.toastContainer.appendChild(toast);
    if (window.lucide) {
      window.lucide.createIcons({ root: toast });
    }

    setTimeout(() => {
      toast.classList.remove('toast-enter');
      toast.classList.add('toast-exit');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  // ---------------------------------------------------------------------------
  // Helper: HTML & JSON Escaping and Syntax Highlighting
  // ---------------------------------------------------------------------------
  function escapeHtml(str) {
    if (typeof str !== 'string') return String(str);
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function syntaxHighlightJson(json) {
    if (typeof json !== 'string') {
      json = JSON.stringify(json, null, 2);
    }
    if (!json) return '';

    const safeJson = escapeHtml(json);
    return safeJson.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = 'json-number';
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'json-key';
          } else {
            cls = 'json-string';
          }
        } else if (/true|false/.test(match)) {
          cls = 'json-boolean';
        } else if (/null/.test(match)) {
          cls = 'json-null';
        }
        return `<span class="${cls}">${match}</span>`;
      }
    );
  }

  // ---------------------------------------------------------------------------
  // Helper: DRF Error Parser
  // ---------------------------------------------------------------------------
  function parseDrfError(data, defaultMsg = 'Request failed') {
    if (!data) return defaultMsg;
    if (typeof data === 'string') return data;

    // Check custom standardized error format
    if (data.error) {
      if (typeof data.error === 'string') return data.error;
      if (data.error.message) {
        let msg = data.error.message;
        if (data.error.details && typeof data.error.details === 'object') {
          const detailParts = [];
          for (const [key, val] of Object.entries(data.error.details)) {
            const valStr = Array.isArray(val) ? val.join(', ') : String(val);
            detailParts.push(`${key}: ${valStr}`);
          }
          if (detailParts.length > 0) {
            msg += ` (${detailParts.join('; ')})`;
          }
        }
        return msg;
      }
    }

    // Check standard DRF detail or non_field_errors
    if (data.detail) {
      return String(data.detail);
    }
    if (data.non_field_errors) {
      return Array.isArray(data.non_field_errors)
        ? data.non_field_errors.join(', ')
        : String(data.non_field_errors);
    }

    // Combine field errors
    const errors = [];
    for (const [key, val] of Object.entries(data)) {
      const valStr = Array.isArray(val) ? val.join(', ') : String(val);
      errors.push(`${key}: ${valStr}`);
    }
    return errors.length > 0 ? errors.join(' | ') : defaultMsg;
  }

  // ---------------------------------------------------------------------------
  // Helper: JWT Payload Decoder (without library)
  // ---------------------------------------------------------------------------
  function decodeJwt(token) {
    try {
      if (!token || typeof token !== 'string') return null;
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const decodedJson = decodeURIComponent(
        atob(payload)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(decodedJson);
    } catch (e) {
      console.warn('Failed to decode JWT:', e);
      return null;
    }
  }

  // ---------------------------------------------------------------------------
  // Core: Unified API Request Runner
  // ---------------------------------------------------------------------------
  async function apiRequest({
    method = 'GET',
    endpoint = '',
    headers = {},
    body = null,
    attachToken = true,
  }) {
    const startTime = performance.now();
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${state.baseUrl.replace(/\/$/, '')}${cleanEndpoint}`;

    const reqHeaders = {
      'Accept': 'application/json',
      ...headers,
    };

    if (body && !reqHeaders['Content-Type']) {
      reqHeaders['Content-Type'] = 'application/json';
    }

    if (attachToken && state.accessToken) {
      reqHeaders['Authorization'] = `Bearer ${state.accessToken}`;
    }

    const reqRecord = {
      id: generateUUID(),
      timestamp: new Date().toLocaleTimeString(),
      method,
      url,
      headers: { ...reqHeaders },
      body: body ? (typeof body === 'string' ? JSON.parse(body) : body) : null,
    };

    let responseStatus = 0;
    let responseStatusText = '';
    let responseHeaders = {};
    let responseData = null;
    let durationMs = 0;
    let isSuccess = false;

    try {
      const fetchOptions = {
        method,
        headers: reqHeaders,
      };

      if (body) {
        fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
      }

      const res = await fetch(url, fetchOptions);
      durationMs = Math.round(performance.now() - startTime);
      responseStatus = res.status;
      responseStatusText = res.statusText || '';

      // Collect response headers
      res.headers.forEach((val, key) => {
        responseHeaders[key] = val;
      });

      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        responseData = await res.json();
      } else {
        const text = await res.text();
        try {
          responseData = JSON.parse(text);
        } catch {
          responseData = text;
        }
      }

      isSuccess = res.ok;
    } catch (err) {
      durationMs = Math.round(performance.now() - startTime);
      responseStatus = 0;
      responseStatusText = 'Network Error';
      responseData = {
        error: 'Network request failed',
        message: err.message || 'Could not connect to SafeGuard Backend. Check if Django server is running.',
        suggestion: `Ensure server is up at ${state.baseUrl} (run: python manage.py runserver)`,
      };
      isSuccess = false;
    }

    const completedRecord = {
      ...reqRecord,
      status: responseStatus,
      statusText: responseStatusText,
      durationMs,
      responseHeaders,
      responseData,
      ok: isSuccess,
    };

    // Update Live Inspector UI
    updateInspector(completedRecord);

    // Save to History
    addHistoryRecord(completedRecord);

    return completedRecord;
  }

  // ---------------------------------------------------------------------------
  // Live Inspector View Updates
  // ---------------------------------------------------------------------------
  function updateInspector(record) {
    dom.inspectUrlText.textContent = record.url;
    dom.inspectLatencyPill.textContent = `${record.durationMs} ms`;

    // Method pill styling
    dom.inspectMethodPill.textContent = record.method;
    const methodColors = {
      GET: 'bg-blue-600/30 text-blue-300 border border-blue-500/40',
      POST: 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40',
      PUT: 'bg-amber-600/30 text-amber-300 border border-amber-500/40',
      PATCH: 'bg-purple-600/30 text-purple-300 border border-purple-500/40',
      DELETE: 'bg-rose-600/30 text-rose-300 border border-rose-500/40',
    };
    dom.inspectMethodPill.className = `text-[11px] font-bold px-2 py-0.5 rounded uppercase font-mono ${methodColors[record.method] || 'bg-slate-700 text-slate-300'}`;

    // Status pill styling
    let statusColor = 'bg-slate-700 text-slate-300';
    if (record.status >= 200 && record.status < 300) {
      statusColor = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
    } else if (record.status >= 300 && record.status < 400) {
      statusColor = 'bg-blue-500/20 text-blue-300 border border-blue-500/40';
    } else if (record.status >= 400 && record.status < 500) {
      statusColor = 'bg-amber-500/20 text-amber-300 border border-amber-500/40';
    } else if (record.status >= 500 || record.status === 0) {
      statusColor = 'bg-rose-500/20 text-rose-300 border border-rose-500/40';
    }
    dom.inspectStatusPill.className = `text-[11px] font-bold px-2.5 py-0.5 rounded font-mono ${statusColor}`;
    dom.inspectStatusPill.textContent = record.status === 0 ? 'ERR' : `${record.status} ${record.statusText}`;

    // Format & Render Body
    if (record.responseData !== null && record.responseData !== undefined) {
      dom.jsonViewer.innerHTML = syntaxHighlightJson(record.responseData);
    } else {
      dom.jsonViewer.textContent = 'No body returned.';
    }

    // Format & Render Sent Request
    dom.requestViewer.innerHTML = syntaxHighlightJson({
      method: record.method,
      url: record.url,
      headers: record.headers,
      body: record.body,
    });

    // Format & Render Headers
    dom.headersViewer.innerHTML = syntaxHighlightJson(record.responseHeaders);
  }

  // ---------------------------------------------------------------------------
  // History Tracker
  // ---------------------------------------------------------------------------
  function addHistoryRecord(record) {
    state.history.unshift({
      id: record.id,
      timestamp: record.timestamp,
      method: record.method,
      url: record.url,
      status: record.status,
      durationMs: record.durationMs,
      reqRecord: {
        method: record.method,
        url: record.url,
        headers: record.headers,
        body: record.body,
      },
      responseHeaders: record.responseHeaders,
      responseData: record.responseData,
    });

    // Keep max 15 records
    if (state.history.length > 15) {
      state.history.pop();
    }
    localStorage.setItem('sg_req_history', JSON.stringify(state.history));
    renderHistoryList();
  }

  function renderHistoryList() {
    if (!dom.historyList) return;
    if (state.history.length === 0) {
      dom.historyList.innerHTML = `<p class="text-slate-500 italic py-4 text-center">No history yet</p>`;
      return;
    }

    dom.historyList.innerHTML = state.history
      .map((item, idx) => {
        const isOk = item.status >= 200 && item.status < 300;
        const pillBg = isOk ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300';
        return `
          <div data-hist-idx="${idx}" class="history-item flex items-center justify-between p-2 rounded-lg bg-slate-900/70 hover:bg-slate-700/60 border border-slate-800 cursor-pointer transition">
            <div class="flex items-center space-x-2 truncate">
              <span class="text-[10px] font-bold uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">${item.method}</span>
              <span class="text-xs text-slate-300 font-mono truncate max-w-[180px]">${item.url.replace(state.baseUrl, '')}</span>
            </div>
            <div class="flex items-center space-x-2 shrink-0">
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded font-mono ${pillBg}">${item.status || 'ERR'}</span>
              <span class="text-[10px] text-slate-400 font-mono">${item.durationMs}ms</span>
            </div>
          </div>
        `;
      })
      .join('');

    // Attach click listeners to historical items
    dom.historyList.querySelectorAll('.history-item').forEach((elem) => {
      elem.addEventListener('click', () => {
        const idx = parseInt(elem.getAttribute('data-hist-idx'), 10);
        const item = state.history[idx];
        if (item) {
          updateInspector({
            method: item.method,
            url: item.url,
            durationMs: item.durationMs,
            status: item.status,
            statusText: '',
            headers: item.reqRecord.headers,
            body: item.reqRecord.body,
            responseHeaders: item.responseHeaders,
            responseData: item.responseData,
          });
          switchInspectorTab('body');
          showToast(`Loaded historical request: ${item.method} ${item.url.replace(state.baseUrl, '')}`, 'info', 2000);
        }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Inspector Tabs Switcher
  // ---------------------------------------------------------------------------
  function switchInspectorTab(target) {
    const tabs = [
      { id: 'body', btn: dom.tabBtnBody, view: dom.viewBody },
      { id: 'req', btn: dom.tabBtnReq, view: dom.viewReq },
      { id: 'headers', btn: dom.tabBtnHeaders, view: dom.viewHeaders },
      { id: 'history', btn: dom.tabBtnHistory, view: dom.viewHistory },
    ];

    tabs.forEach((t) => {
      if (t.id === target) {
        t.btn.className = 'font-semibold text-indigo-400 border-b-2 border-indigo-500 pb-1 flex items-center space-x-1';
        t.view.classList.remove('hidden');
      } else {
        t.btn.className = 'text-slate-400 hover:text-slate-200 pb-1 flex items-center space-x-1';
        t.view.classList.add('hidden');
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Backend Connection Health & Ping
  // ---------------------------------------------------------------------------
  async function checkBackendHealth(silent = false) {
    setBackendStatus('checking', 'Checking...');

    const res = await apiRequest({
      method: 'GET',
      endpoint: '/api/v1/health/',
      attachToken: false,
    });

    if (res.ok && res.responseData && res.responseData.status === 'healthy') {
      setBackendStatus('online', 'Online (200 OK)');
      dom.healthCardStatus.textContent = 'Healthy';
      dom.healthCardStatus.className = 'text-sm font-semibold text-emerald-400 mt-1 block';
      dom.healthCardLatency.textContent = `${res.durationMs} ms`;
      dom.healthCardVersion.textContent = res.responseData.version || '1.0.0';
      if (!silent) {
        showToast(`Backend connection healthy (${res.durationMs} ms)`, 'success');
      }
      return true;
    } else {
      setBackendStatus('offline', 'Offline');
      dom.healthCardStatus.textContent = 'Unreachable';
      dom.healthCardStatus.className = 'text-sm font-semibold text-rose-400 mt-1 block';
      dom.healthCardLatency.textContent = '-- ms';
      if (!silent) {
        showToast('Backend offline. Make sure Django server is running.', 'error');
      }
      return false;
    }
  }

  function setBackendStatus(stateName, label) {
    dom.backendStatusText.textContent = label;
    if (stateName === 'online') {
      dom.backendStatusDot.className = 'w-2 h-2 rounded-full bg-emerald-400 status-pill-online';
      dom.backendStatusPill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30';
    } else if (stateName === 'offline') {
      dom.backendStatusDot.className = 'w-2 h-2 rounded-full bg-rose-500 status-pill-offline';
      dom.backendStatusPill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-rose-500/10 text-rose-300 border border-rose-500/30';
    } else {
      dom.backendStatusDot.className = 'w-2 h-2 rounded-full bg-amber-400 animate-pulse';
      dom.backendStatusPill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-700/50 text-slate-300 border border-slate-600/50';
    }
  }

  // ---------------------------------------------------------------------------
  // Token Lifecycle & UI Updates
  // ---------------------------------------------------------------------------
  function saveTokens(access, refresh, userObj = null) {
    if (access) {
      state.accessToken = access;
      localStorage.setItem('sg_access_token', access);
      dom.accessTokenDisplay.value = access;
    }
    if (refresh) {
      state.refreshToken = refresh;
      localStorage.setItem('sg_refresh_token', refresh);
      dom.refreshTokenDisplay.value = refresh;
    }
    if (userObj) {
      state.currentUser = userObj;
      localStorage.setItem('sg_current_user', JSON.stringify(userObj));
    }
    updateTokenUi();
  }

  function clearTokens() {
    state.accessToken = '';
    state.refreshToken = '';
    state.currentUser = null;
    localStorage.removeItem('sg_access_token');
    localStorage.removeItem('sg_refresh_token');
    localStorage.removeItem('sg_current_user');

    dom.accessTokenDisplay.value = '';
    dom.refreshTokenDisplay.value = '';
    if (state.tokenTimerInterval) {
      clearInterval(state.tokenTimerInterval);
      state.tokenTimerInterval = null;
    }
    updateTokenUi();
    showToast('Tokens cleared from local state', 'info');
  }

  function updateTokenUi() {
    if (state.accessToken) {
      dom.authStatusUser.textContent = state.currentUser ? state.currentUser.email || state.currentUser.display_name : 'Authenticated';
      dom.quickLogoutBtn.classList.remove('hidden');
      dom.profileAuthIndicator.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span class="text-emerald-400 font-medium">Token Active</span>
      `;

      // Decode JWT Payload
      const decoded = decodeJwt(state.accessToken);
      if (decoded) {
        dom.decodedTokenBox.classList.remove('hidden');
        dom.decodedPayloadContent.innerHTML = syntaxHighlightJson(decoded);

        // Expiry management
        if (decoded.exp) {
          updateTokenTimer(decoded.exp);
          if (!state.tokenTimerInterval) {
            state.tokenTimerInterval = setInterval(() => {
              if (state.accessToken) {
                const curDecoded = decodeJwt(state.accessToken);
                if (curDecoded && curDecoded.exp) {
                  updateTokenTimer(curDecoded.exp);
                }
              }
            }, 1000);
          }
        }
      } else {
        dom.decodedTokenBox.classList.add('hidden');
      }
    } else {
      dom.authStatusUser.textContent = 'Not logged in';
      dom.quickLogoutBtn.classList.add('hidden');
      dom.tokenExpiryBadge.textContent = 'No Active Token';
      dom.tokenExpiryBadge.className = 'text-xs px-2.5 py-1 rounded-md bg-slate-700 text-slate-300 font-mono';
      dom.decodedTokenBox.classList.add('hidden');
      dom.profileAuthIndicator.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-slate-500"></span>
        <span>Needs Bearer Token</span>
      `;
      if (state.tokenTimerInterval) {
        clearInterval(state.tokenTimerInterval);
        state.tokenTimerInterval = null;
      }
    }
  }

  function updateTokenTimer(expSeconds) {
    const nowSeconds = Math.floor(Date.now() / 1000);
    const diff = expSeconds - nowSeconds;

    if (diff <= 0) {
      dom.tokenExpiryBadge.textContent = 'Token Expired';
      dom.tokenExpiryBadge.className = 'text-xs px-2.5 py-1 rounded-md bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono font-bold';
      dom.tokenTimerText.textContent = '(Expired)';
      dom.tokenTimerText.className = 'text-rose-400 font-bold';
    } else {
      const minutes = Math.floor(diff / 60);
      const seconds = diff % 60;
      const formatted = `${minutes}m ${seconds}s`;
      dom.tokenExpiryBadge.textContent = `Expires in ${formatted}`;
      dom.tokenExpiryBadge.className = 'text-xs px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono';
      dom.tokenTimerText.textContent = `Valid for: ${formatted}`;
      dom.tokenTimerText.className = 'text-emerald-400';
    }
  }

  // ---------------------------------------------------------------------------
  // Authentication Actions
  // ---------------------------------------------------------------------------
  async function handleRegister(e) {
    e.preventDefault();
    const email = dom.regEmail.value.trim();
    const displayName = dom.regDisplayName.value.trim();
    const phoneNumber = dom.regPhone.value.trim();
    const preferredLanguage = dom.regLang.value;
    const password = dom.regPassword.value;
    const passwordConfirm = dom.regPasswordConfirm.value;

    if (password !== passwordConfirm) {
      showToast('Validation Error: Passwords do not match!', 'error');
      return;
    }

    const payload = {
      email,
      display_name: displayName,
      phone_number: phoneNumber,
      preferred_language: preferredLanguage,
      password,
      password_confirm: passwordConfirm,
    };

    const res = await apiRequest({
      method: 'POST',
      endpoint: '/api/v1/auth/register/',
      body: payload,
      attachToken: false,
    });

    if (res.ok) {
      showToast(`User registered successfully! (${email})`, 'success');
      state.lastRegistered = { email, password };
      localStorage.setItem('sg_last_registered', JSON.stringify(state.lastRegistered));

      // Auto fill login form
      dom.loginEmail.value = email;
      dom.loginPassword.value = password;
      showToast('Login form auto-filled with registered credentials. Ready to login!', 'info', 5000);
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Registration failed');
      showToast(`Registration failed: ${errorMsg}`, 'error', 6000);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    const email = dom.loginEmail.value.trim();
    const password = dom.loginPassword.value;

    const payload = { email, password };

    const res = await apiRequest({
      method: 'POST',
      endpoint: '/api/v1/auth/token/',
      body: payload,
      attachToken: false,
    });

    if (res.ok && res.responseData) {
      const access = res.responseData.access;
      const refresh = res.responseData.refresh;

      saveTokens(access, refresh, { email });
      showToast(`Login successful! Tokens acquired for ${email}`, 'success');

      // Automatically fetch current profile to populate data
      fetchUserProfile(true);
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Invalid email or password');
      showToast(`Login failed: ${errorMsg}`, 'error', 5000);
    }
  }

  async function handleRefreshToken() {
    if (!state.refreshToken) {
      showToast('No refresh token available! Please login first.', 'warning');
      return;
    }

    const res = await apiRequest({
      method: 'POST',
      endpoint: '/api/v1/auth/token/refresh/',
      body: { refresh: state.refreshToken },
      attachToken: false,
    });

    if (res.ok && res.responseData) {
      const newAccess = res.responseData.access;
      const newRefresh = res.responseData.refresh || state.refreshToken;
      saveTokens(newAccess, newRefresh);
      showToast('JWT Access Token refreshed successfully!', 'success');
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Token refresh failed');
      showToast(`Refresh failed: ${errorMsg}`, 'error', 5000);
    }
  }

  async function handleBlacklistToken() {
    if (!state.refreshToken) {
      showToast('No refresh token available to blacklist.', 'warning');
      return;
    }

    const res = await apiRequest({
      method: 'POST',
      endpoint: '/api/v1/auth/token/blacklist/',
      body: { refresh: state.refreshToken },
      attachToken: true,
    });

    if (res.ok) {
      showToast('Refresh token blacklisted successfully! User logged out.', 'success');
      clearTokens();
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Blacklist failed');
      showToast(`Blacklist failed: ${errorMsg}`, 'error');
    }
  }

  // ---------------------------------------------------------------------------
  // Profile Management
  // ---------------------------------------------------------------------------
  async function fetchUserProfile(silent = false) {
    if (!state.accessToken) {
      showToast('Please login first to view user profile.', 'warning');
      return;
    }

    const res = await apiRequest({
      method: 'GET',
      endpoint: '/api/v1/users/me/',
      attachToken: true,
    });

    if (res.ok && res.responseData) {
      const u = res.responseData;
      renderProfileData(u);
      if (!silent) {
        showToast('Profile fetched successfully!', 'success');
      }
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Failed to fetch profile');
      showToast(`Profile fetch error: ${errorMsg}`, 'error');
    }
  }

  function renderProfileData(user) {
    dom.profileDetailsCard.classList.remove('hidden');

    const name = user.display_name || user.email || 'User';
    dom.profileAvatar.textContent = name.charAt(0).toUpperCase();
    dom.profileNameDisplay.textContent = user.display_name || 'No Name Set';
    dom.profileEmailDisplay.textContent = user.email || '--';
    dom.profileRoleBadge.textContent = user.role || 'USER';
    dom.profilePhoneDisplay.textContent = user.phone_number || 'None';
    dom.profileLangDisplay.textContent = user.preferred_language === 'hi' ? 'Hindi (hi)' : 'English (en)';
    dom.profileGuardianDisplay.textContent = user.is_guardian_managed ? 'Yes' : 'No';

    const prof = user.profile || {};
    dom.profileBioDisplay.textContent = prof.bio || 'No bio provided';
    dom.profileEmergencyMsgDisplay.textContent = prof.emergency_message || 'No emergency message configured';

    // Populate edit form
    dom.editDisplayName.value = user.display_name || '';
    dom.editPhone.value = user.phone_number || '';
    dom.editLang.value = user.preferred_language || 'en';
    dom.editBio.value = prof.bio || '';
    dom.editEmergencyMessage.value = prof.emergency_message || '';

    // Update state currentUser with latest info
    state.currentUser = user;
    localStorage.setItem('sg_current_user', JSON.stringify(user));
    dom.authStatusUser.textContent = user.email || user.display_name;
  }

  async function handleUpdateProfile(e) {
    e.preventDefault();
    if (!state.accessToken) {
      showToast('Authentication required. Please login first.', 'warning');
      return;
    }

    const payload = {
      display_name: dom.editDisplayName.value.trim(),
      phone_number: dom.editPhone.value.trim(),
      preferred_language: dom.editLang.value,
      profile: {
        bio: dom.editBio.value.trim(),
        emergency_message: dom.editEmergencyMessage.value.trim(),
      },
    };

    const res = await apiRequest({
      method: 'PATCH',
      endpoint: '/api/v1/users/me/',
      body: payload,
      attachToken: true,
    });

    if (res.ok && res.responseData) {
      showToast('Profile updated successfully!', 'success');
      renderProfileData(res.responseData);
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Failed to update profile');
      showToast(`Update error: ${errorMsg}`, 'error', 5000);
    }
  }

  // ---------------------------------------------------------------------------
  // SOS Emergency Trigger
  // ---------------------------------------------------------------------------
  async function handleTriggerSos(e) {
    e.preventDefault();

    if (!state.accessToken) {
      showToast('Authentication required to trigger SOS! Please login first.', 'warning', 5000);
      switchTab('tab-auth');
      return;
    }

    const idempotencyKey = dom.sosIdempotencyKey.value.trim() || generateUUID();
    const eventType = dom.sosEventType.value;
    const notes = dom.sosNotes.value.trim();
    const lat = parseFloat(dom.sosLatitude.value);
    const lng = parseFloat(dom.sosLongitude.value);
    const acc = parseFloat(dom.sosAccuracy.value) || 10.0;

    const payload = {
      idempotency_key: idempotencyKey,
      event_type: eventType,
      notes,
    };

    if (!isNaN(lat) && !isNaN(lng)) {
      payload.latitude = lat;
      payload.longitude = lng;
      payload.accuracy_meters = acc;
    }

    const res = await apiRequest({
      method: 'POST',
      endpoint: '/api/v1/emergencies/sos/',
      body: payload,
      attachToken: true,
    });

    if (res.ok) {
      const eventId = res.responseData ? res.responseData.id || 'Created' : 'Sent';
      showToast(`🚨 SOS Triggered Successfully! Event ID: ${eventId}`, 'success', 6000);
      // Auto-regenerate idempotency key for next trigger
      dom.sosIdempotencyKey.value = generateUUID();
    } else {
      const errorMsg = parseDrfError(res.responseData, 'SOS trigger failed');
      showToast(`🚨 SOS Failed: ${errorMsg}`, 'error', 6000);
    }
  }

  async function handleFetchEmergencyHistory() {
    if (!state.accessToken) {
      showToast('Login required to fetch emergency history.', 'warning');
      return;
    }

    const res = await apiRequest({
      method: 'GET',
      endpoint: '/api/v1/emergencies/',
      attachToken: true,
    });

    if (res.ok) {
      const count = Array.isArray(res.responseData) ? res.responseData.length : '0';
      showToast(`Fetched ${count} emergency record(s)`, 'info');
    } else {
      const errorMsg = parseDrfError(res.responseData, 'Failed to fetch history');
      showToast(`Error: ${errorMsg}`, 'error');
    }
  }

  // ---------------------------------------------------------------------------
  // Custom Request Explorer
  // ---------------------------------------------------------------------------
  async function handleCustomRequest(e) {
    e.preventDefault();
    const method = dom.customMethod.value;
    const path = dom.customPath.value.trim();
    const attachToken = dom.customAttachToken.checked;
    let body = null;

    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      const rawBody = dom.customBody.value.trim();
      if (rawBody) {
        try {
          body = JSON.parse(rawBody);
        } catch {
          showToast('Invalid JSON in request body!', 'error');
          return;
        }
      }
    }

    const res = await apiRequest({
      method,
      endpoint: path,
      body,
      attachToken,
    });

    if (res.ok) {
      showToast(`Custom request completed (${res.status})`, 'success');
    } else {
      showToast(`Custom request returned error (${res.status})`, 'warning');
    }
  }

  // ---------------------------------------------------------------------------
  // Tab Navigation Handling
  // ---------------------------------------------------------------------------
  function switchTab(tabId) {
    dom.tabBtns.forEach((btn) => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('tab-active');
        btn.classList.remove('text-slate-400');
        btn.classList.add('text-slate-200');
      } else {
        btn.classList.remove('tab-active');
        btn.classList.remove('text-slate-200');
        btn.classList.add('text-slate-400');
      }
    });

    dom.tabPanes.forEach((pane) => {
      if (pane.id === tabId) {
        pane.classList.remove('hidden');
        pane.classList.add('block');
      } else {
        pane.classList.remove('block');
        pane.classList.add('hidden');
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Theme Toggle (Dark / Light)
  // ---------------------------------------------------------------------------
  function setTheme(theme) {
    state.theme = theme;
    localStorage.setItem('sg_theme', theme);

    if (theme === 'light') {
      document.body.classList.add('light-theme');
      dom.themeIcon.setAttribute('data-lucide', 'moon');
    } else {
      document.body.classList.remove('light-theme');
      dom.themeIcon.setAttribute('data-lucide', 'sun');
    }
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  // ---------------------------------------------------------------------------
  // Location Preset Helper
  // ---------------------------------------------------------------------------
  const locationPresets = {
    delhi: { lat: 28.613939, lng: 77.209021, acc: 10 },
    mumbai: { lat: 19.075983, lng: 72.877655, acc: 15 },
    bengaluru: { lat: 12.971599, lng: 77.594566, acc: 12 },
  };

  function setLocationPreset(presetKey) {
    const loc = locationPresets[presetKey];
    if (loc) {
      dom.sosLatitude.value = loc.lat;
      dom.sosLongitude.value = loc.lng;
      dom.sosAccuracy.value = loc.acc;
      showToast(`Location set to ${presetKey.toUpperCase()}`, 'info', 2000);
    }
  }

  function getDeviceCoordinates() {
    if (!navigator.geolocation) {
      showToast('Geolocation is not supported by this browser.', 'warning');
      return;
    }
    showToast('Requesting device GPS coordinates...', 'info', 2000);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        dom.sosLatitude.value = pos.coords.latitude.toFixed(6);
        dom.sosLongitude.value = pos.coords.longitude.toFixed(6);
        dom.sosAccuracy.value = Math.round(pos.coords.accuracy);
        showToast('Device GPS coordinates captured!', 'success');
      },
      (err) => {
        showToast(`GPS Error: ${err.message}`, 'warning');
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  }

  // ---------------------------------------------------------------------------
  // Clipboard Copy Helper
  // ---------------------------------------------------------------------------
  async function copyText(text, label = 'Copied to clipboard!') {
    if (!text) {
      showToast('Nothing to copy!', 'warning');
      return;
    }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        textarea.remove();
      }
      showToast(label, 'success', 2000);
    } catch {
      showToast('Failed to copy to clipboard', 'error');
    }
  }

  // ---------------------------------------------------------------------------
  // Event Listeners Binding
  // ---------------------------------------------------------------------------
  function initEventListeners() {
    // Base URL change
    dom.baseUrlInput.addEventListener('change', () => {
      let val = dom.baseUrlInput.value.trim();
      if (!val.startsWith('http://') && !val.startsWith('https://')) {
        val = `http://${val}`;
        dom.baseUrlInput.value = val;
      }
      state.baseUrl = val;
      localStorage.setItem('sg_base_url', val);
      updateDocLinks();
      checkBackendHealth();
    });

    // Ping button
    dom.pingBtn.addEventListener('click', () => checkBackendHealth());
    dom.runHealthCheckBtn.addEventListener('click', () => checkBackendHealth());

    // Theme toggle
    dom.themeToggleBtn.addEventListener('click', () => {
      setTheme(state.theme === 'dark' ? 'light' : 'dark');
    });

    // Quick logout
    dom.quickLogoutBtn.addEventListener('click', () => {
      if (confirm('Log out and clear stored tokens?')) {
        clearTokens();
      }
    });

    // Tab buttons
    dom.tabBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        switchTab(btn.getAttribute('data-tab'));
      });
    });

    // Inspector Sub-tabs
    dom.tabBtnBody.addEventListener('click', () => switchInspectorTab('body'));
    dom.tabBtnReq.addEventListener('click', () => switchInspectorTab('req'));
    dom.tabBtnHeaders.addEventListener('click', () => switchInspectorTab('headers'));
    dom.tabBtnHistory.addEventListener('click', () => switchInspectorTab('history'));

    // Copy JSON in inspector
    dom.copyJsonBtn.addEventListener('click', () => {
      copyText(dom.jsonViewer.textContent, 'JSON response copied!');
    });

    // Clear history
    dom.clearHistoryBtn.addEventListener('click', () => {
      state.history = [];
      localStorage.removeItem('sg_req_history');
      renderHistoryList();
      showToast('Request history cleared', 'info');
    });

    // Registration auto-fill sample
    dom.fillSampleRegisterBtn.addEventListener('click', () => {
      const rand = Math.floor(1000 + Math.random() * 9000);
      dom.regEmail.value = `tester_${rand}@safeguard.local`;
      dom.regDisplayName.value = `Test User ${rand}`;
      dom.regPhone.value = `+9198${rand}43210`;
      dom.regLang.value = 'en';
      dom.regPassword.value = 'SafePass123!';
      dom.regPasswordConfirm.value = 'SafePass123!';
      showToast('Sample registration data generated', 'info', 2000);
    });

    // Forms
    dom.registerForm.addEventListener('submit', handleRegister);
    dom.loginForm.addEventListener('submit', handleLogin);
    dom.refreshTokenBtn.addEventListener('click', handleRefreshToken);
    dom.blacklistTokenBtn.addEventListener('click', handleBlacklistToken);
    dom.clearTokensBtn.addEventListener('click', clearTokens);

    // Copy tokens
    dom.copyAccessTokenBtn.addEventListener('click', () => {
      copyText(dom.accessTokenDisplay.value, 'Access Token copied!');
    });
    dom.copyRefreshTokenBtn.addEventListener('click', () => {
      copyText(dom.refreshTokenDisplay.value, 'Refresh Token copied!');
    });

    // Profile
    dom.fetchProfileBtn.addEventListener('click', () => fetchUserProfile());
    dom.profileUpdateForm.addEventListener('submit', handleUpdateProfile);

    // SOS
    dom.regenerateIdempotencyBtn.addEventListener('click', () => {
      dom.sosIdempotencyKey.value = generateUUID();
      showToast('New idempotency UUID generated', 'info', 1500);
    });
    dom.locPresetBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        setLocationPreset(btn.getAttribute('data-preset'));
      });
    });
    dom.getCurrentGeoBtn.addEventListener('click', getDeviceCoordinates);
    dom.sosForm.addEventListener('submit', handleTriggerSos);
    dom.fetchEmergencyHistoryBtn.addEventListener('click', handleFetchEmergencyHistory);

    // Custom request presets & form
    dom.customChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        dom.customPath.value = chip.getAttribute('data-fill-path');
      });
    });
    dom.prettifyJsonBtn.addEventListener('click', () => {
      try {
        const parsed = JSON.parse(dom.customBody.value);
        dom.customBody.value = JSON.stringify(parsed, null, 2);
      } catch {
        showToast('Cannot prettify: Invalid JSON format', 'warning');
      }
    });
    dom.customReqForm.addEventListener('submit', handleCustomRequest);
  }

  function updateDocLinks() {
    const base = state.baseUrl.replace(/\/$/, '');
    if (dom.swaggerLink) dom.swaggerLink.href = `${base}/api/docs/`;
    if (dom.openSwaggerBtn) dom.openSwaggerBtn.href = `${base}/api/docs/`;
    if (dom.openAdminBtn) dom.openAdminBtn.href = `${base}/admin/`;
  }

  // ---------------------------------------------------------------------------
  // Initialization Routine
  // ---------------------------------------------------------------------------
  function init() {
    // Restore Base URL
    dom.baseUrlInput.value = state.baseUrl;
    updateDocLinks();

    // Set Initial Idempotency Key
    dom.sosIdempotencyKey.value = generateUUID();

    // Restore Tokens & User State
    if (state.accessToken) {
      dom.accessTokenDisplay.value = state.accessToken;
    }
    if (state.refreshToken) {
      dom.refreshTokenDisplay.value = state.refreshToken;
    }
    updateTokenUi();

    // Restore Last Registered User to Login Form if available
    if (state.lastRegistered && state.lastRegistered.email) {
      dom.loginEmail.value = state.lastRegistered.email;
      dom.loginPassword.value = state.lastRegistered.password || '';
    }

    // Set Theme
    setTheme(state.theme);

    // Render History
    renderHistoryList();

    // Initialize Event Listeners
    initEventListeners();

    // Initialize Icons
    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Health check ping on start
    setTimeout(() => {
      checkBackendHealth(true);
    }, 400);
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
