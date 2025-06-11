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

local function proxy_with_fallback()
    local start_index = get_start_index()
    local total_nodes = #backend_nodes
    ngx.log(ngx.ERR, "[Proxy] Start index: ", start_index)

    for i = 0, total_nodes - 1 do
        local index = ((start_index + i - 1) % total_nodes) + 1
        local node = backend_nodes[index]
        ngx.log(ngx.ERR, "[Proxy] Trying backend #", index, ": ", node)

        local client = http.new()
        client:set_timeout(5000)

        local body_data = ngx.req.get_body_data()
        local res, err = client:request_uri(node .. ngx.var.request_uri, {
            method = ngx.req.get_method(),
            headers = ngx.req.get_headers(),
            body = body_data,
            keepalive_timeout = 60,
            keepalive_pool = 10,
            ssl_verify = false
        })

        if res then
            ngx.log(ngx.ERR, "[Proxy] Response status from ", node, ": ", res.status)
        else
            ngx.log(ngx.ERR, "[Proxy] Request error to ", node, ": ", err)
        end

        if res and res.status < 500 then
            ngx.status = res.status
            for k, v in pairs(res.headers) do
                ngx.header[k] = v
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
