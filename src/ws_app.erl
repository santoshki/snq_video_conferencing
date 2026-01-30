-module(ws_app).
-behaviour(application).

-export([start/2, stop/1]).

start(_Type, _Args) ->
    Dispatch = cowboy_router:compile([
        {'_', [
            {"/ws", ws_handler, #{}}
        ]}
    ]),

    {ok, _} = cowboy:start_clear(ws_http_listener,
        [{port, 8080}],
        #{env => #{dispatch => Dispatch}}
    ),

    ws_sup:start_link().

stop(_State) ->
    ok.
