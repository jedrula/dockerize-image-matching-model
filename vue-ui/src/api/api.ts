import axios, { type AxiosProgressEvent } from "axios";

export const apiUrl = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: apiUrl,
});

// matching api
export const findMatch = async (
  file: File,
  folder: string,
  onUploadProgress: (progressEvent: AxiosProgressEvent) => void
) => {
  const formData = new FormData();
  formData.append("image1", file);

  try {
    const response = await api.post(
      `/find_match?folder_path=${folder}`,
      formData,
      {
        onUploadProgress,
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};

export const findMatchingMatrix = async (
  imageData: string,
  folder: string,
  onUploadProgress: (progressEvent: AxiosProgressEvent) => void
) => {
  try {
    const response = await api.post(
      `/find_matching_matrix`,
      {
        folder_path: folder,
        image_data: imageData,
      },
      {
        onUploadProgress,
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error finding matching matrix:", error);
    throw error;
  }
};

export const getBestMatchPreview = async (
  file: File,
  bestMatch: string,
  onUploadProgress: (progressEvent: AxiosProgressEvent) => void
) => {
  const formData = new FormData();
  formData.append("image1", file);

  try {
    const response = await api.post(
      `/get_matching_with?image_path=${encodeURIComponent(bestMatch)}`,
      formData,
      {
        responseType: "blob",
        onUploadProgress,
      }
    );
    return response;
  } catch (error) {
    console.error("Error fetching best match preview:", error);
    throw error;
  }
};

export const getMatchingMatrix = async (file1: File, file2: File) => {
  const formData = new FormData();
  formData.append("image1", file1);
  formData.append("image2", file2);

  try {
    const response = await api.post("/get_matching_matrix", formData);
    return response.data;
  } catch (error) {
    console.error("Error fetching matching matrix with files:", error);
    throw error;
  }
};

export const getRegion = async (region) => {
  const response = await api.get(`/region/${region}`);
  console.log(response.data);
  return response.data;
};

export const createRegion = async (data) => {
  const response = await api.post(`/region`, data);
  console.log(response.data);
  return response.data;
};

export const getCrag = async (crag) => {
  const response = await api.get(`/crag/${crag}`);
  console.log(response.data);
  return response.data;
};

export const updateCrag = async (crag, data) => {
  const response = await api.put(`/crag/${crag}`, data);
  console.log(response.data);
  return response.data;
};

export const addCrag = async ({
  region_name,
  ...cragData
}: {
  region_name: string;
}) => {
  const response = await api.post(`${region_name}/crag`, cragData);
  console.log(response.data);
  return response.data;
};
