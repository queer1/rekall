# Rekall Memory Forensics
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

__author__ = "Michael Cohen <scudette@google.com>"

from rekall.plugins.darwin import common
from rekall.plugins.darwin import lsof


class DarwinArp(common.DarwinPlugin):
    """Show information about arp tables."""

    __name = "arp"

    def render(self, renderer):
        renderer.table_header(
            [("IP Addr", "ip_addr", "20"),
             ("MAC Addr", "mac", "18"),
             ("Interface", "interface", "9"),
             ("Sent", "sent", "8"),
             ("Recv", "recv", "8"),
             ("Time", "timestamp", "24"),
             ("Expires", "expires", "8"),
             ("Delta", "delta", "8"),
             ])

        arp_cache = self.profile.get_constant_object(
            "_llinfo_arp",
            target="Pointer",
            target_args=dict(
                target="llinfo_arp"
                )
            )

        while arp_cache:
            entry = arp_cache.la_rt

            renderer.table_row(
                entry.source_ip,
                entry.dest_ip,
                entry.name,
                entry.sent,
                entry.rx,
                entry.base_calendartime,
                entry.rt_expire,
                entry.delta
                )

            arp_cache = arp_cache.la_le.le_next


class DarwinRoute(common.DarwinPlugin):
    """Show routing table."""

    __name = "route"

    RNF_ROOT = 2

    def rn_walk_tree(self, h):
        """Walks the radix tree starting from the header h.

        This function is taken from
        xnu-2422.1.72/bsd/net/radix.c: rn_walk_tree()

        Which is why it does not conform to the style guide.

        Note too that the darwin source code abuses C macros:

        #define rn_dupedkey     rn_u.rn_leaf.rn_Dupedkey
        #define rn_key          rn_u.rn_leaf.rn_Key
        #define rn_mask         rn_u.rn_leaf.rn_Mask
        #define rn_offset       rn_u.rn_node.rn_Off
        #define rn_left         rn_u.rn_node.rn_L
        #define rn_right        rn_u.rn_node.rn_R

        And then the original code does:
        rn = rn.rn_left

        So we replace these below.
        """
        rn = h.rnh_treetop

        seen = set()

        # First time through node, go left */
        while rn.rn_bit >= 0:
            rn = rn.rn_u.rn_node.rn_L

        while rn and rn not in seen:
            base = rn

            seen.add(rn)

            # If at right child go back up, otherwise, go right
            while (rn.rn_parent.rn_u.rn_node.rn_R == rn and
                   not rn.rn_flags & self.RNF_ROOT):
                rn = rn.rn_parent

            # Find the next *leaf* to start from
            rn = rn.rn_parent.rn_u.rn_node.rn_R
            while rn.rn_bit >= 0:
                rn = rn.rn_u.rn_node.rn_L

            next = rn

            # Process leaves
            while True:
                rn = base
                if not rn:
                    break

                base = rn.rn_u.rn_leaf.rn_Dupedkey
                if not rn.rn_flags & self.RNF_ROOT:
                    yield rn

            rn = next
            if rn.rn_flags & self.RNF_ROOT:
                return

    def render(self, renderer):
        renderer.table_header(
            [("Source IP", "source", "20"),
             ("Dest IP", "dest", "20"),
             ("Interface", "interface", "9"),
             ("Sent", "sent", "8"),
             ("Recv", "recv", "8"),
             ("Time", "timestamp", "24"),
             ("Expires", "expires", "8"),
             ("Delta", "delta", "8"),
             ])

        route_tables = self.profile.get_constant_object(
            "_rt_tables",
            target="Array",
            target_args=dict(
                count=32,
                target="Pointer",
                target_args=dict(
                    target="radix_node_head"
                    )
                )
            )

        for node in self.rn_walk_tree(route_tables[2]):
            rentry = node.dereference_as("rtentry")

            renderer.table_row(
                rentry.source_ip,
                rentry.dest_ip,
                rentry.name,
                rentry.sent, rentry.rx,
                rentry.base_calendartime,
                rentry.rt_expire,
                rentry.delta)


class DarwinIFConfig(common.DarwinPlugin):
    """List network interface information."""

    __name = "ifconfig"

    def render(self, renderer):
        renderer.table_header([("Interface", "interface", "10"),
                               ("Address", "address", "20")])

        ifnet_head = self.profile.get_constant_object(
            "_dlil_ifnet_head",
            target="Pointer",
            target_args=dict(
                target="ifnet"
                )
            )

        for interface in ifnet_head.walk_list("if_link.tqe_next"):
            for address in interface.if_addrhead.tqh_first.walk_list(
                "ifa_link.tqe_next"):
                name = "%s%d" % (interface.if_name.deref(),
                                      interface.if_unit)

                renderer.table_row(
                    name, address.ifa_addr.deref())


class DarwinIPFilters(common.DarwinPlugin):
    """Check IP Filters for hooks."""

    __name = "ip_filters"

    def render(self, renderer):
        renderer.table_header([
                ("Context", "context", "10"),
                ("Filter", "filter", "16"),
                ("Handler", "handler", "[addrpad]"),
                ("Symbol", "symbol", "20")])

        lsmod = self.session.plugins.lsmod(session=self.session)

        for list_name in ["_ipv4_filters", "_ipv6_filters"]:
            filter_list = self.profile.get_constant_object(
                list_name, target="ipfilter_list")

            for item in filter_list.tqh_first.walk_list("ipf_link.tqe_next"):
                filter = item.ipf_filter
                name = filter.name.deref()
                handler = filter.ipf_input.deref()
                renderer.table_row("INPUT", name, handler,
                                   lsmod.ResolveSymbolName(handler))

                handler = filter.ipf_output.deref()
                renderer.table_row("OUTPUT", name, handler,
                                   lsmod.ResolveSymbolName(handler))

                handler = filter.ipf_detach.deref()
                renderer.table_row("DETACH", name, handler,
                                   lsmod.ResolveSymbolName(handler))


class DarwinEntityNetstat(common.DarwinPlugin):
    """List per process network connections."""

    __name = "enetstat"

    def render(self, renderer):
        connections = self.session.get_entities(entity.Connection)

        # Group connections by protocol/addressing family.
        inet_by_proto = {}
        unix_socks = []

        for connection in connections:
            if connection.addressing_family in ["AF_INET", "AF_INET6"]:
                proto = connection.protocol
                inet_by_proto.setdefault(proto, []).append(connection)
            elif connection.addressing_family == "AF_UNIX":
                unix_socks.append(connection)

        # Render inet protos first, in alphabetical order (like netstat).
        renderer.section("Active Internet connections")
        renderer.table_header([
            ("Proto", "proto", "14"),
            ("SAddr", "saddr", "30"),
            ("SPort", "sport", "8"),
            ("DAddr", "daddr", "30"),
            ("DPort", "dport", "5"),
            ("State", "state", "15"),
            ("Pid", "pid", "8"),
            ("Comm", "comm", "20"),
        ])

        # Sort by inet protos, then PID.
        for proto, connections in sorted(inet_by_proto.iteritems()):
            for connection in sorted(
                connections,
                key=lambda x: (x.handle.process.pid, x.key_obj)):
                renderer.table_row(
                    proto,
                    connection.src_address,
                    connection.src_port,
                    connection.dst_address,
                    connection.dst_port,
                    connection.state,
                    connection.handle.process.pid,
                    connection.handle.process.command,
                )

        # Render the UNIX sockets.
        renderer.section("Active UNIX domain sockets")
        renderer.table_header([
            ("Address", "address", "14"),
            ("Conn", "conn", "14"),
            ("Type", "type", "10"),
            ("Vnode", "vnode", "14"),
            ("Path", "path", "60"),
            ("Pid", "pid", "8"),
            ("Comm", "comm", "20"),
        ])

        for connection in sorted(
            unix_socks,
            key=lambda x: (x.handle.process.pid, x.key_obj)):
            renderer.table_row(
                connection.source,
                connection.destination,
                connection.entity_type,
                "0x%x" % int(connection.key_obj.vnode),
                connection.entity_name,
                connection.handle.process.pid,
                connection.handle.process.command,
            )


class DarwinNetstat(lsof.DarwinLsof):
    """List per process network connections."""

    __name = "netstat"

    def sockets(self):
        for open_file in self.lsof():
            if open_file["fileproc"].fg_type != "DTYPE_SOCKET":
                continue

            sock = open_file["fileproc"].autocast_fg_data()
            if sock.addressing_family in ["AF_INET", "AF_INET6", "AF_UNIX"]:
                yield open_file

    def render(self, renderer):
        inet_by_proto = {}
        unix_socks = []

        # Group sockets by protocol/addressing family.
        for open_file in self.sockets():
            sock = open_file["fileproc"].autocast_fg_data()
            proto = sock.l4_protocol

            if proto:
                inet_by_proto.setdefault(proto, []).append((sock, open_file))
            else:
                unix_socks.append((sock, open_file))

        # Render all inet protos in alphabetical order (like netstat).
        renderer.section("Active Internet connections")
        renderer.table_header([
            ("Proto", "proto", "14"),
            ("SAddr", "saddr", "30"),
            ("SPort", "sport", "8"),
            ("DAddr", "daddr", "30"),
            ("DPort", "dport", "5"),
            ("State", "state", "15"),
            ("Pid", "pid", "8"),
            ("Comm", "comm", "20"),
        ])

        for proto, sockets in sorted(inet_by_proto.iteritems()):
            for sock, open_file in sockets:
                renderer.table_row(
                    proto,
                    sock.src_addr,
                    sock.src_port,
                    sock.dst_addr,
                    sock.dst_port,
                    sock.tcp_state,
                    open_file["proc"].pid,
                    open_file["proc"].p_comm,
                )

        # Render the UNIX sockets.
        renderer.section("Active UNIX domain sockets")
        renderer.table_header([
            ("Address", "address", "14"),
            ("Conn", "conn", "14"),
            ("Type", "type", "10"),
            ("Vnode", "vnode", "14"),
            ("Path", "path", "60"),
            ("Pid", "pid", "8"),
            ("Comm", "comm", "20"),
        ])

        for sock, open_file in unix_socks:
            renderer.table_row(
                "0x%x" % int(sock.so_pcb),
                "0x%x" % int(sock.unp_conn),
                sock.human_type,
                "0x%x" % int(sock.vnode),
                sock.human_name,
                open_file["proc"].pid,
                open_file["proc"].p_comm,
            )
