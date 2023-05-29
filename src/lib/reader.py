import numpy as np
import pandas as pd

from typing import overload


class Reader:
    fn: str
    ws: pd.DataFrame
    
    data_scale: int
    
    dates: np.ndarray
    line_series: pd.DataFrame
    scatter_series: pd.DataFrame
    
    def __init__(self, fn: str) -> None:
        self.update(fn)
        # interp = self.interp_by_series(
        #     self.line_series.iloc[:, 0].to_numpy(), self.scatter_series.iloc[:, 0].to_numpy()
        # )
        # print(f"{self.to_timestamp(interp[0])}\n{interp[1]}")
        
    def update(self, fn: str) -> None:
        self.fn = fn
        self.ws = pd.read_excel(fn, sheet_name=0)
        self._collect()
        
    def mask(self, series: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Mask a series by the dates stored within this Reader object.

        Args:
            series (np.ndarray): The series to be masked.

        Returns:
            tuple[np.ndarray, np.ndarray]: Two same length fully-finite ndarrays that correspond 1:1.
        """
        mask = np.isfinite(series)  # masks the NaN values that exist within the series
        return self.dates[mask], series[mask]
    
    def interp_by_series(self, lsu: np.ndarray, ss: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # given a full line series and a set of scatter points, locate the scatter point positions on the line
        ls_dates, ls = self.mask(lsu)
        ss_dates, ss_values = [], []
        
        for i in range(self.data_scale):
            if isinstance(ss[i], str):
                ss_dates.append(date := self.dates[i])
                if date in ls_dates:
                    idx = np.where(ls_dates == date)[0][0]
                    ss_values.append(ls[idx])
                else:
                    ss_values.append(np.interp(date, ls_dates, ls))
                
        return np.array(ss_dates).astype(np.int64), np.array(ss_values).astype(np.float64)
    
    @overload
    def to_timestamp(self, f: np.ndarray) -> np.ndarray:
        ...
        
    @overload
    def to_timestamp(self, f: np.int64 | np.float64) -> pd.Timestamp:
        ...
    
    def to_timestamp(self, f):
        if isinstance(f, np.ndarray):
            converted = []
            
            for val in f:
                converted.append(pd.to_datetime(val, unit='s'))
                
            return np.array(converted)
        else:
            return pd.to_datetime(f, unit='s')
        
    def get_dates(self) -> np.ndarray:
        return self.dates
    
    def get_lines(self) -> pd.DataFrame:
        return self.line_series
    
    def get_scatter(self) -> pd.DataFrame:
        return self.scatter_series
        
    def _collect(self) -> None:
        # collecting dates
        dates = [data.timestamp() for data in self.ws.iloc[:, 0].tolist()]
        self.dates = np.array(dates).astype(np.int64)
        self.data_scale = len(self.dates)
        # ^ : indicates getting all rows, the 0 indicates all row values from col. 0
        
        # collecting line series data
        self.line_series = self.ws.select_dtypes(include='float64')
        self.line_series.index = self.dates  # type: ignore
        
        # collecting scatter series data
        self.scatter_series = self.ws.select_dtypes(include='object')
        self.scatter_series.index = self.dates  # type: ignore
        # setting the indexes for dataframes upsets Pylance, so we ignore  
