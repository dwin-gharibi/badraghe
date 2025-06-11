local limit_store = ngx.shared.rate_limit_store
local ip = ngx.var.remote_addr
local key = "limit:" .. ip

local reqs = limit_store:get(key)
if reqs then
    if reqs >= 20 then
        ngx.status = 429
        ngx.say("Rate limit exceeded")
        return ngx.exit(429)
    else
        limit_store:incr(key, 1)
    end
else
    limit_store:set(key, 1, 60)
end
