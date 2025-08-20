import React, { useEffect, useState } from 'react';
import {
  SimpleGrid,
  Text,
  useColorModeValue,
  Button,
  FormControl,
  FormLabel,
  Textarea,
  Input,
  useToast,
  Select
} from '@chakra-ui/react';

import { Flex, Box, Icon, Spacer } from "@chakra-ui/react";
import Card from 'components/card/Card';
import { updateUserProfile, getUserProfile } from 'services/api';
import { useNavigate } from 'react-router-dom';
import { FaUserEdit } from 'react-icons/fa';

export default function ProfileEdit() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    country: '',
    state: '',
    city: '',
    address: '',
    zip_code: '',
    date_of_birth: '',
    gender: '',
    bio: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const textColorPrimary = useColorModeValue('secondaryGray.900', 'white');
  const textColorSecondary = 'gray.400';
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const response = await getUserProfile();
        setFormData({
          first_name: response.first_name || '',
          last_name: response.last_name || '',
          email: response.email || '',
          phone: response.phone || '',
          country: response.country || '',
          state: response.state || '',
          city: response.city || '',
          address: response.address || '',
          zip_code: response.zip_code || '',
          date_of_birth: response.date_of_birth || '',
          gender: response.gender || '',
          bio: response.bio || '',
        });
      } catch (err) {
        setError(err.message || 'Failed to fetch profile');
        toast({
          title: 'Error',
          description: err.message || 'Failed to fetch profile',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/auth/sign-in');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [toast, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await updateUserProfile(formData);
      toast({
        title: 'Profile Updated',
        description: 'Your profile has been successfully updated.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      navigate('/user/profile');
    } catch (err) {
      setError(err.message || 'Failed to update profile');
      toast({
        title: 'Error',
        description: err.message || 'Failed to update profile',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Text>Loading...</Text>;
  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <Card mb={{ base: '0px', '2xl': '20px' }}>
      <Text color={textColorPrimary} fontWeight="bold" fontSize="2xl" mt="10px" mb="4px">
        <Icon as={FaUserEdit} color="brand.500" w={5} h={5} mx={2}/> Edit Profile
      </Text>
      <Text color={textColorSecondary} fontSize="md" me="26px" mb="40px" mx={2}>
        Update your personal details below.
      </Text>
      <SimpleGrid columns={{ sm: 1, md: 2 }} gap="20px">
        <FormControl>
          <FormLabel>First Name</FormLabel>
          <Input
            name="first_name"
            value={formData.first_name}
            onChange={handleInputChange}
            placeholder="First Name"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Last Name</FormLabel>
          <Input
            name="last_name"
            value={formData.last_name}
            onChange={handleInputChange}
            placeholder="Last Name"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Email</FormLabel>
          <Input
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Email"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Phone</FormLabel>
          <Input
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            placeholder="Phone"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Country</FormLabel>
          <Input
            name="country"
            value={formData.country}
            onChange={handleInputChange}
            placeholder="Country"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>State</FormLabel>
          <Input
            name="state"
            value={formData.state}
            onChange={handleInputChange}
            placeholder="State"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>City</FormLabel>
          <Input
            name="city"
            value={formData.city}
            onChange={handleInputChange}
            placeholder="City"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Address</FormLabel>
          <Input
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            placeholder="Address"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Zip Code</FormLabel>
          <Input
            name="zip_code"
            value={formData.zip_code}
            onChange={handleInputChange}
            placeholder="Zip Code"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Date of Birth</FormLabel>
          <Input
            name="date_of_birth"
            type="date"
            value={formData.date_of_birth}
            onChange={handleInputChange}
            placeholder="Date of Birth"
            isDisabled={loading}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Gender</FormLabel>
          <Select
            name="gender"
            value={formData.gender}
            onChange={handleInputChange}
            placeholder="Select gender"
            isDisabled={loading}
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </Select>

        </FormControl>
        <FormControl>
          <FormLabel>Bio</FormLabel>
          <Textarea
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
            placeholder="Bio"
            isDisabled={loading}
          />
        </FormControl>
      </SimpleGrid>
      <Flex justifyContent="flex-end" mt="20px">
        <Button
          variant="brand"
          rounded="full"
          onClick={handleSubmit}
          isDisabled={loading}
          isLoading={loading}
        >
          Save Changes
        </Button>
        <Button
          variant="outline"
          rounded="full"
          ml="10px"
          onClick={() => navigate('/user/profile')}
          isDisabled={loading}
        >
          Cancel
        </Button>
      </Flex>
    </Card>
  );
}