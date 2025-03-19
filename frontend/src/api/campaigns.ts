import axios from 'axios';

interface CampaignParams {
  limit?: number;
  skip?: number;
  active_only?: boolean;
  npo_id?: number;
}

export const getCampaigns = async (params: CampaignParams = {}) => {
  const token = localStorage.getItem('token');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  return axios.get('/api/v1/campaigns', {
    headers,
    params,
  });
};

export const getCampaign = async (id: number) => {
  const token = localStorage.getItem('token');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  return axios.get(`/api/v1/campaigns/${id}`, { headers });
};

export const createCampaign = async (data: any) => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authentication required');

  return axios.post('/api/v1/campaigns', data, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const updateCampaign = async (id: number, data: any) => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authentication required');

  return axios.put(`/api/v1/campaigns/${id}`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const deleteCampaign = async (id: number) => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Authentication required');

  return axios.delete(`/api/v1/campaigns/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}; 