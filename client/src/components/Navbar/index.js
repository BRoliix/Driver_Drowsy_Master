import React from "react";
import { Nav, NavLink, NavMenu }
	from "./NavbarElements";

const Navbar = () => {
	return (
		<>
			<Nav>
				<NavMenu>
					<NavLink to="/session" activeStyle>
						Sessions
					</NavLink>
					<NavLink to="/sos" activeStyle>
						SOS
					</NavLink>
					<NavLink to="/test" activeStyle>
						TEST
					</NavLink>

				</NavMenu>
			</Nav>
			<br/><br/>		</>
	);
};

export default Navbar;
