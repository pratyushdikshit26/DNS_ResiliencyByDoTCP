package dnsserver

import (
        "github.com/miekg/dns"
)


var MyMsgAcceptFunc dns.MsgAcceptFunc = defaultMsgAcceptFunc

//accept all
func defaultMsgAcceptFunc(dh dns.Header) dns.MsgAcceptAction {
        return dns.MsgAccept
}