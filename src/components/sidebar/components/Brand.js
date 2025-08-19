import React from "react";

import { Flex, useColorModeValue, Image } from "@chakra-ui/react";
import logoSvg from "assets/img/logos/logo-badraghe.svg";
import { HSeparator } from "components/separator/Separator";

export function SidebarBrand() {
  let logoColor = useColorModeValue("navy.700", "white");

  return (
    <Flex align='center' direction='column'>
      <Image h="36px" src={logoSvg} alt="Logo" />
      <HSeparator my='20px' />
    </Flex>
  );
}

export default SidebarBrand;
