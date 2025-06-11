local http = require("resty.http")
local lock = require("resty.lock")

local rr_dict = ngx.shared.rr_counter
local backend_nodes = {
    "https://api1.badraghe.dwin.codes",
    "https://api2.badraghe.dwin.codes",
    "https://api3.badraghe.dwin.codes"
}

local function get_start_index()
    ngx.log(ngx.ERR, "[RR] Attempting to get start index")

    local lock_obj, err = lock:new("rr_counter")
    if not lock_obj then
        ngx.log(ngx.ERR, "[RR] Failed to create lock: ", err)
        return 1
    end

    local elapsed, err = lock_obj:lock("backend_lock")
    if not elapsed then
        ngx.log(ngx.ERR, "[RR] Failed to acquire lock: ", err)
        return 1
    end

    local counter = rr_dict:get("counter") or 0
    ngx.log(ngx.ERR, "[RR] Current counter: ", counter)

    local index = (counter % #backend_nodes) + 1
    rr_dict:set("counter", counter + 1)
    ngx.log(ngx.ERR, "[RR] New index: ", index, " Updated counter: ", counter + 1)

    local ok, unlock_err = lock_obj:unlock()
    if not ok then
        ngx.log(ngx.ERR, "[RR] Failed to unlock: ", unlock_err)
    else
        ngx.log(ngx.ERR, "[RR] Lock released")
    end

    return index
end

local function sanitize_headers(headers, backend_host)
    local new_headers = {}
    for k, v in pairs(headers) do
        local lower_k = k:lower()
        if lower_k ~= "host" and lower_k ~= "connection" and lower_k ~= "content-length" and lower_k ~= "accept-encoding" then
            new_headers[k] = v
        end
    end
    new_headers["Host"] = backend_host:gsub("^https?://", "")
    new_headers["Accept-Encoding"] = "gzip, deflate, br"
    return new_headers
end

local function proxy_with_fallback()
    local start_index = get_start_index()
    local total_nodes = #backend_nodes
    ngx.log(ngx.ERR, "[Proxy] Start index: ", start_index)

    local req_method = ngx.req.get_method()
    local body_data = ngx.req.get_body_data()
    local req_headers = ngx.req.get_headers()

    for i = 0, total_nodes - 1 do
        local index = ((start_index + i - 1) % total_nodes) + 1
        local node = backend_nodes[index]
        ngx.log(ngx.ERR, "[Proxy] Trying backend #", index, ": ", node)

        local client = http.new()
        client:set_timeout(5000)

        local sanitized_headers = sanitize_headers(req_headers, node)
        ngx.log(ngx.ERR, "[Proxy] Forwarding headers to ", node, ": ", require("cjson").encode(sanitized_headers))

        local res, err = client:request_uri(node .. ngx.var.request_uri, {
            method = req_method,
            headers = sanitized_headers,
            body = body_data,
            keepalive_timeout = 60,
            keepalive_pool = 10,
            ssl_verify = false,
            version = 1.1
        })

        if res then
            ngx.log(ngx.ERR, "[Proxy] Response status from ", node, ": ", res.status)
            ngx.log(ngx.ERR, "[Proxy] Response headers: ", require("cjson").encode(res.headers))
        else
            ngx.log(ngx.ERR, "[Proxy] Request error to ", node, ": ", err)
        end

        if res and res.status < 500 then
            ngx.status = res.status
            for k, v in pairs(res.headers) do
                local lk = k:lower()
                if lk ~= "transfer-encoding" and lk ~= "connection" then
                    ngx.header[k] = v
                end
            end
            ngx.say(res.body)
            ngx.log(ngx.ERR, "[Proxy] Successfully proxied request to ", node)
            return
        else
            ngx.log(ngx.ERR, "[Proxy] Failed to proxy to ", node, ": ", err or ("HTTP " .. (res and res.status or "nil")))
        end
    end

    ngx.status = 502
    ngx.say("All backend nodes failed")
    ngx.log(ngx.ERR, "[Proxy] All backend nodes failed")
end

proxy_with_fallback()
