// src/utils/api.ts
export interface Restaurant {
    RestaurantID: number;
    RestaurantName: string;
    Location: string;
    Stars: number;
    Cuisine: string;
    Image?: string;
    Corkage?: boolean;
    Parking?: boolean;
    NumberOfSeats?: number;
    Latitude: number;
    Longitude: number;
    Menu: string;
    RegistrationDate: string;
    CommissionFee: number;
    ImageURL?: string;
  }
  
  const API_BASE = 'http://223.130.155.88:3000/api';
  
  export const fetchRestaurants = async (): Promise<Restaurant[]> => {
    const res = await fetch(`${API_BASE}/restaurants`);
    if (!res.ok) throw new Error('레스토랑 목록 불러오기 실패');
    return await res.json();
  };

  export const fetchRestaurantById = async (id: number): Promise<Restaurant> => {
    const res = await fetch(`${API_BASE}/restaurants/${id}`);
    if (!res.ok) throw new Error('레스토랑 상세정보 불러오기 실패');
    return await res.json();
  };
  
  