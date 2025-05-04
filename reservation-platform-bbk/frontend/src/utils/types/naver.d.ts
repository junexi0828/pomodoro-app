export {}; // 글로벌 선언이므로 반드시 필요

declare global {
  interface Window {
    naver: {
      maps: {
        Map: new (element: HTMLElement, options: any) => any;
        LatLng: new (lat: number, lng: number) => any;
        Marker: new (options: any) => any;
        InfoWindow: new (options: any) => any;
        Event: {
          addListener: (
            target: any,
            eventName: string,
            listener: (...args: any[]) => void
          ) => void;
        };
      };
    };
  }
}
