pub const DEFAULT_PORTS: [u16; 3] = [5173, 3000, 8080];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ProtocolFilter {
    pub tcp: bool,
    pub udp: bool,
}

impl ProtocolFilter {
    pub fn from_flags(tcp: bool, udp: bool) -> Self {
        if tcp || udp {
            Self { tcp, udp }
        } else {
            Self {
                tcp: true,
                udp: true,
            }
        }
    }
}
