import React from "react";

import { Flex, useColorModeValue } from "@chakra-ui/react";

import { HSeparator } from "components/separator/Separator";

export function SidebarBrand() {
  let logoColor = useColorModeValue("navy.700", "white");

  return (
    <Flex align='center' direction='column'>
      <HSeparator mb='20px' />
    </Flex>
  );
}

export default SidebarBrand;
