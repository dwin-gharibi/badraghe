local http = require("resty.http")
local lock = require("resty.lock")

local rr_dict = ngx.shared.rr_counter
local backend_nodes = {
    "https://api1.badraghe.dwin.codes",
    "https://api2.badraghe.dwin.codes",
    "https://api3.badraghe.dwin.codes"
}

local function get_start_index()
    local lock_obj, err = lock:new("rr_counter")
    if not lock_obj then
        ngx.log(ngx.ERR, "Failed to create lock: ", err)
        return 1
    end

    local elapsed, err = lock_obj:lock("backend_lock")
    if not elapsed then
        ngx.log(ngx.ERR, "Failed to acquire lock: ", err)
        return 1
    end

    local counter = rr_dict:get("counter") or 0
    local index = (counter % #backend_nodes) + 1
    rr_dict:set("counter", counter + 1)

    local ok, unlock_err = lock_obj:unlock()
    if not ok then
        ngx.log(ngx.ERR, "Failed to unlock: ", unlock_err)
    end

    return index
end

local function proxy_with_fallback()
    local start_index = get_start_index()
    local total_nodes = #backend_nodes

    for i = 0, total_nodes - 1 do
        local index = ((start_index + i - 1) % total_nodes) + 1
        local node = backend_nodes[index]
        local client = http.new()

        local res, err = client:request_uri(node .. ngx.var.request_uri, {
            method = ngx.req.get_method(),
            headers = ngx.req.get_headers(),
            body = ngx.req.get_body_data(),
            keepalive_timeout = 60,
            keepalive_pool = 10
        })

        if res and res.status < 500 then
            ngx.status = res.status
            for k, v in pairs(res.headers) do
                ngx.header[k] = v
            end
            ngx.say(res.body)
            return
        else
            ngx.log(ngx.ERR, "Failed to proxy to ", node, ": ", err or ("HTTP " .. (res and res.status or "nil")))
        end
    end

    ngx.status = 502
    ngx.say("All backend nodes failed")
end

proxy_with_fallback()
