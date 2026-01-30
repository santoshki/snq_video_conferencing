-module(ws_handler).
-behaviour(cowboy_websocket).

-export([
    init/2,
    websocket_init/1,
    websocket_handle/2,
    websocket_info/2,
    terminate/3
]).

-record(state, {
    room,
    user
}).

init(Req, _Opts) ->
    {cowboy_websocket, Req, #{}}.

websocket_init(State) ->
    {ok, State}.

websocket_handle({text, Msg}, State) ->
    Data = jsx:decode(Msg, [return_maps]),

    case maps:get(<<"type">>, Data) of
        <<"join">> ->
            Room = maps:get(<<"room">>, Data),
            User = maps:get(<<"user">>, Data),
            room_registry:join(Room, self(), User),
            {ok, State#{room => Room, user => User}};

        Type when Type == <<"offer">>;
                 Type == <<"answer">>;
                 Type == <<"ice">>;
                 Type == <<"chat">> ->
            room_registry:broadcast(
                State#state.room,
                self(),
                Msg
            ),
            {ok, State};

        _ ->
            {ok, State}
    end.

websocket_info({send, Msg}, State) ->
    {reply, {text, Msg}, State};

websocket_info(_, State) ->
    {ok, State}.

terminate(_Reason, _Req, State) ->
    case State of
        #{room := Room} ->
            room_registry:leave(Room, self());
        _ -> ok
    end,
    ok.
